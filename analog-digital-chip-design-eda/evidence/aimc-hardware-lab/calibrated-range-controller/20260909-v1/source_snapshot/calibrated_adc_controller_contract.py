"""Review-only ADC bank protocol and range descriptors, not a hardware ISA."""
import math
import struct

RECORD = struct.Struct("<HHHBBd")


def pack_ranges(contract):
    ranges = contract["adc_range"]["ranges"]
    bits = contract["profile"]["adc_bits"]
    if not 2 <= bits <= 16:
        raise ValueError("Invalid ADC precision")
    inputs,outputs=contract["weight_shape_input_output"]
    nr,nc=contract["profile"]["tile_rows"],contract["profile"]["tile_columns"]
    if min(inputs,outputs,nr,nc)<=0:
        raise ValueError("Invalid tile geometry")
    expected=[(r,c) for r in range(0,inputs,nr) for c in range(0,outputs,nc)]
    if [(r["row"],r["column"]) for r in ranges]!=expected or len(ranges)!=contract["logical_tiles"]:
        raise ValueError("Range table does not cover the canonical tile map")
    records = []
    coordinates = set()
    for tile, row in enumerate(ranges):
        bound = row["selected_bound"]
        r,c = row["row"],row["column"]
        if not math.isfinite(bound) or bound <= 0 or (r,c) in coordinates:
            raise ValueError("Invalid or duplicate range descriptor")
        coordinates.add((r,c))
        records.append(RECORD.pack(tile,r,c,bits,0,bound))
    return b"".join(records)


def unpack_ranges(data):
    if not data or len(data)%RECORD.size:
        raise ValueError("Truncated descriptor table")
    result=[]
    coordinates=set()
    for offset in range(0,len(data),RECORD.size):
        tile,r,c,bits,reserved,bound=RECORD.unpack_from(data,offset)
        if tile!=len(result) or reserved or not 2<=bits<=16 or not math.isfinite(bound) or bound<=0 or (r,c) in coordinates:
            raise ValueError("Invalid descriptor encoding")
        coordinates.add((r,c))
        result.append({"tile_id":tile,"row":r,"column":c,"adc_bits":bits,"bound_model_units":bound})
    return result


def make_program(descriptors,banks=8,lanes=16,columns=128):
    if banks<1 or lanes<1 or columns<1:
        raise ValueError("Resources must be positive")
    events=[]
    for start in range(0,len(descriptors),banks):
        active=descriptors[start:start+banks]
        for operation in ["select_tile","configure_range","range_ready","load_dac","array_ready"]:
            for bank,descriptor in enumerate(active):
                events.append({"operation":operation,"bank":bank,"tile":descriptor["tile_id"]})
        for round_index in range((columns+lanes-1)//lanes):
            for bank,descriptor in enumerate(active):
                events.append({"operation":"read_adc","bank":bank,"tile":descriptor["tile_id"],
                               "round":round_index,"columns":min(lanes,columns-round_index*lanes)})
        for bank,descriptor in enumerate(active):
            events.append({"operation":"accumulate","bank":bank,"tile":descriptor["tile_id"]})
    return events


def replay(program,descriptors,banks=8,lanes=16,columns=128):
    """Validate assumed ready acknowledgements; performs no physical I/O."""
    states={};completed=set();conversions=0;configurations=0
    expected_tiles={d["tile_id"] for d in descriptors}
    for event in program:
        bank,tile,operation=event["bank"],event["tile"],event["operation"]
        if not 0<=bank<banks or tile not in expected_tiles:
            raise ValueError("Unknown bank or tile")
        if operation=="select_tile":
            if bank in states and states[bank]["phase"]!="done":
                raise ValueError("Bank reused before accumulation")
            if tile in completed or any(s["tile"]==tile and s["phase"]!="done" for s in states.values()):
                raise ValueError("Duplicate tile dispatch")
            states[bank]={"tile":tile,"phase":"selected","round":0,"columns":0}
            continue
        state=states.get(bank)
        if state is None or state["tile"]!=tile:
            raise ValueError("Unbound or stale bank acknowledgement")
        transitions={"configure_range":("selected","configured"),"range_ready":("configured","range_ready"),
                     "load_dac":("range_ready","loaded"),"array_ready":("loaded","array_ready")}
        if operation in transitions:
            before,after=transitions[operation]
            if state["phase"]!=before:
                raise ValueError("Range/array readiness ordering violation")
            state["phase"]=after
            configurations+=operation=="configure_range"
        elif operation=="read_adc":
            width=min(lanes,columns-state["columns"])
            if state["phase"]!="array_ready" or event["round"]!=state["round"] or width<=0 or event["columns"]!=width:
                raise ValueError("ADC read before ready or invalid column coverage")
            state["round"]+=1;state["columns"]+=width;conversions+=width
        elif operation=="accumulate":
            if state["phase"]!="array_ready" or state["columns"]!=columns:
                raise ValueError("Incomplete ADC readout")
            state["phase"]="done";completed.add(tile)
        else:
            raise ValueError("Unsupported review operation")
    if completed!=expected_tiles:
        raise ValueError("Incomplete tile coverage")
    return {"status":"reference_ordering_pass","completed_tiles":len(completed),"range_configurations":configurations,
            "adc_conversions":conversions,"physical_io_performed":False,"readiness_events":"assumed acknowledgements"}
