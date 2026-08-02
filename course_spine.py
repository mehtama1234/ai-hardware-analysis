COURSE_TITLE = "AI Hardware From First Principles"
COURSE_SUBTITLE = (
    "A plain-language course spine for MLSys, ISCA, MICRO, HPCA, ASPLOS, DAC, ISSCC, "
    "Hot Chips, SC, VLSID, CGO, ICCAD, DATE, OSDI, ATC, and FCCM."
)

INTRO = [
    "AI hardware is about one simple pressure: modern models want more work than ordinary machines can cheaply provide.",
    "The work is not only arithmetic. The machine must store numbers, move them, line them up, reuse them, check them, protect them, cool the chip, and keep many chips acting like one larger machine.",
    "This page explains the conference map in ordinary words. It treats each topic as a physical question first, then shows why the same question appears across chips, compilers, datacenters, devices, and AI systems.",
]

SECTIONS = [
    {
        "kicker": "Start",
        "title": "The Whole Field Is About Work, Movement, And Limits",
        "summary": "A model is a long recipe for turning numbers into new numbers. Hardware decides how fast and cheaply that recipe can run.",
        "body": [
            "An AI model looks abstract on paper, but on a machine it becomes a stream of simple actions: read numbers, multiply them, add them, write results, repeat. Each action costs time and energy.",
            "The surprising cost is often not the multiply. It is moving the numbers to the place where the multiply happens. Moving data across a chip, between memory and a processor, or across a network can cost more than the arithmetic itself.",
            "This is why the conferences keep returning to the same question: where should the numbers live, where should the work happen, and how can the machine avoid moving data that does not matter?",
        ],
        "applications": [
            "Training large models needs many chips to share work without waiting on each other.",
            "Phone and laptop AI needs useful results inside a small power and heat budget.",
            "Scientific computing needs large machines where memory, storage, and networks stay balanced.",
        ],
    },
    {
        "kicker": "Numbers",
        "title": "Using Smaller Numbers Saves Space And Time",
        "summary": "If a model can use shorter numbers without losing the answer, the machine moves less data and uses less energy.",
        "body": [
            "A number can be stored with many bits or few bits. More bits can represent more detail. Fewer bits take less space, move faster, and use less energy.",
            "The hard question is where detail matters. Some parts of a model need careful numbers. Other parts tolerate rounding. Hardware papers study how far the numbers can be shortened before the answer changes too much.",
            "This is not only a math trick. It changes memory size, wire traffic, chip area, battery life, heat, and how many requests a server can handle.",
        ],
        "applications": [
            "Inference servers use shorter weights and caches to fit more users on the same hardware.",
            "Edge devices use smaller numbers to keep speech, vision, and language models local.",
            "Custom chips add arithmetic units built for the exact number sizes the model can tolerate.",
        ],
    },
    {
        "kicker": "Memory",
        "title": "The Memory Wall Is A Distance Problem",
        "summary": "The machine slows down when useful numbers are far from the place that needs them.",
        "body": [
            "A processor may be ready to work, but the data may be sitting far away. That wait is the memory wall. It is a wall because adding more arithmetic does not help if the arithmetic units are waiting for data.",
            "Caches, high-bandwidth memory, processing near memory, and better layouts are all attempts to shorten the trip. The goal is to reuse data nearby and avoid long movement whenever possible.",
            "The same idea appears at many scales: inside a core, across chip memory, across GPU memory, across server memory, and across storage.",
        ],
        "applications": [
            "Language model serving is often limited by reading the stored context again and again.",
            "Graph and database work can be limited by scattered memory reads.",
            "Scientific simulations can spend more time moving arrays than computing on them.",
        ],
    },
    {
        "kicker": "Topology",
        "title": "Topology Means Which Parts Are Connected And Which Paths Data Can Take",
        "summary": "In hardware, topology is the shape of connections: wires, networks, memory banks, chiplets, racks, and failure paths.",
        "body": [
            "In plain words, topology asks what connects to what. Can this chip reach that memory directly, or must the data pass through another chip? Is there one path or many? If one link fails, does the machine split into isolated parts?",
            "On a chip, topology includes where blocks sit and how wires run between them. Long wires cost time and energy. Crowded crossings make layout harder. A better placement can make the same design faster without changing the arithmetic.",
            "In a datacenter, topology includes how GPUs, CPUs, memory, storage, and network switches connect. A training job can slow down if many chips must share one narrow path. A better network shape lets more chips exchange data at once.",
            "Topology also appears in reliability. If one memory bank, link, or server fails, the system needs another path or a way to keep enough pieces connected to finish the job.",
        ],
        "applications": [
            "Chip design uses topology when placing compute blocks, memory blocks, and wires.",
            "Supercomputers use topology when choosing network shapes that avoid traffic jams.",
            "Chiplet systems use topology when deciding how many small dies should connect and where.",
            "Security uses topology when deciding which data paths must be isolated from an attacker.",
        ],
    },
    {
        "kicker": "Skipping",
        "title": "The Fastest Work Is Work The Machine Does Not Do",
        "summary": "Many model numbers are zero, repeated, unneeded, or less important for a given input.",
        "body": [
            "If a number is zero, multiplying by it adds no useful information. If two requests share the same prefix, computing the shared part twice wastes time. If only a few experts are needed for one token, running every expert wastes energy.",
            "Skipping is easy to say and hard to build. The machine must know what can be skipped, skip it without spending more overhead than it saves, and still produce the correct answer.",
            "Hardware, compilers, and serving systems all participate. A model may expose the possible skips, but the system must turn them into real saved time.",
        ],
        "applications": [
            "Sparse models route only part of the model for each input.",
            "Serving systems reuse cached work when many users ask related questions.",
            "Accelerators skip zero or near-zero values when the format makes those values easy to detect.",
        ],
    },
    {
        "kicker": "Compilers",
        "title": "A Compiler Is The Translator Between Idea And Machine",
        "summary": "The model says what should be computed; the compiler decides how to arrange that work on real hardware.",
        "body": [
            "A model description is not yet a good machine schedule. The compiler breaks work into pieces, chooses memory layouts, fuses steps, places loops, assigns registers, and decides which hardware unit should do which part.",
            "This matters because two programs that compute the same answer can have very different costs. One may move data constantly. Another may keep useful values nearby and reuse them.",
            "Compiler papers matter more as hardware becomes less uniform. CPUs, GPUs, custom accelerators, memory engines, and network devices all have different strengths. The translator has to know the body it is targeting.",
        ],
        "applications": [
            "ML compilers turn model graphs into kernels that fit the target chip.",
            "Hardware design tools turn a high-level circuit description into gates and wires.",
            "Serving systems compile requests into batches and schedules that reduce waiting.",
        ],
    },
    {
        "kicker": "Many Chips",
        "title": "A Cluster Is A Machine Made Of Smaller Machines",
        "summary": "Large AI runs need many chips to share one job without wasting time waiting.",
        "body": [
            "One chip is not enough for the largest training and serving jobs. The system becomes a group of chips, boards, racks, switches, storage devices, and cooling equipment.",
            "The hard part is coordination. Each chip must receive the right data, finish its share, exchange results, and keep pace with the rest. If one part waits, the whole job may slow down.",
            "This is why interconnects, scheduling, storage, and failure recovery are part of AI hardware. The computer is no longer just a chip. It is the whole path from power to cooling to network to software.",
        ],
        "applications": [
            "Training frontier models depends on fast links between accelerators.",
            "Inference services depend on routing requests to available memory and compute.",
            "High-performance computing depends on storage and networks that keep processors fed.",
        ],
    },
    {
        "kicker": "Correctness",
        "title": "Fast Is Not Enough If The Answer Cannot Be Trusted",
        "summary": "Hardware can fail silently, and design mistakes can be built into millions of chips.",
        "body": [
            "A hardware error is different from a software error. Once a chip is fabricated, fixing it can be costly or impossible. Even after the design is correct, radiation, wear, heat, and manufacturing variation can flip bits or change timing.",
            "Correctness work asks how to know the machine did what it was supposed to do. Reliability work asks how the machine keeps going when parts fail. The two are connected: both are about protecting the answer.",
            "AI adds pressure because models can tolerate some numeric noise but not arbitrary failure. The system needs to know which errors matter, which can be corrected, and which require stopping.",
        ],
        "applications": [
            "Datacenters use error correction and checkpointing to survive long training runs.",
            "Chip design uses verification to catch mistakes before manufacturing.",
            "Safety-critical devices need bounds on timing, power, and failure behavior.",
        ],
    },
    {
        "kicker": "Security",
        "title": "The Machine Must Protect The Work It Runs",
        "summary": "Speedups can create side doors if data, timing, or shared hardware leaks information.",
        "body": [
            "A shared machine can leak information even when programs never directly read each other's data. Timing, cache use, power, faults, or speculative work can reveal clues.",
            "Security papers study how attacks use the physical and shared parts of the machine. They also study defenses: isolation, checking, safer instructions, safer memory, and designs that remove the signal an attacker would measure.",
            "The tension is that protection costs resources. The design has to keep the machine useful while closing the paths that leak or corrupt information.",
        ],
        "applications": [
            "Cloud AI services need isolation between users sharing accelerators.",
            "Phones and laptops need to protect private data while running local models.",
            "Critical systems need hardware that resists both software attacks and physical probing.",
        ],
    },
    {
        "kicker": "Fields",
        "title": "Why This Matters Outside Hardware",
        "summary": "Hardware choices shape what AI, robotics, science, medicine, and public systems can afford to do.",
        "body": [
            "A better algorithm may not matter if it cannot run within the time, memory, energy, and cost limits of the real system. Hardware sets those limits.",
            "Robotics needs efficient chips because a robot carries its own power and must react quickly. Speech and vision need local chips because some tasks must run with low delay and private data. Search and recommendation need serving systems that handle many users without wasting power.",
            "Topology connects this hardware story to other fields. In networks, it is which machines can reach each other. In city systems, it is how routes connect. In biology, it is how folded structures and pathways are connected. In AI hardware, it is the shape that data can move through.",
        ],
        "applications": [
            "Medicine gains faster imaging, lab automation, and local privacy-preserving models.",
            "Climate and science gain larger simulations and more efficient data analysis.",
            "Consumer devices gain AI features that run without sending every request to a server.",
            "Public infrastructure gains systems that can monitor, predict, and respond under real power and cost limits.",
        ],
    },
]

READING_PATH = [
    ("index.html", "Master narrative"),
    ("deepdives.html", "Theme deep dives"),
    ("grand-synthesis.html", "Grand synthesis"),
    ("heatmap.html", "Theme and venue map"),
    ("explorer.html", "Paper explorer"),
    ("compiler.html", "Compiler mechanisms"),
]
