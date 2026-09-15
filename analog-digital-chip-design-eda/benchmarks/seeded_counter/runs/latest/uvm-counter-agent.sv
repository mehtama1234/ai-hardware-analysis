// Generated UVM scaffold; review and compile against the target UVM library.
`include "uvm_macros.svh"
import uvm_pkg::*;

interface counteragent_if(input logic clk);
  logic clk;
  logic rst;
  logic enable;
  logic counter_q;
endinterface

class counteragent_transaction extends uvm_sequence_item;
  `uvm_object_utils(counteragent_transaction)
  rand logic clk;
  rand logic rst;
  rand logic enable;
  rand logic counter_q;
  function new(string name="counteragent_transaction"); super.new(name); endfunction
endclass

class counteragent_agent extends uvm_agent;
  `uvm_component_utils(counteragent_agent)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

// Dependency order: interface -> transaction -> driver/monitor -> agent -> scoreboard -> env.
class counteragent_driver extends uvm_driver #(counteragent_transaction);
  `uvm_component_utils(counteragent_driver)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class counteragent_monitor extends uvm_monitor;
  `uvm_component_utils(counteragent_monitor)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class counteragent_scoreboard extends uvm_scoreboard;
  `uvm_component_utils(counteragent_scoreboard)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class counteragent_env extends uvm_env;
  `uvm_component_utils(counteragent_env)
  counteragent_agent agent;
  counteragent_scoreboard scoreboard;
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass
