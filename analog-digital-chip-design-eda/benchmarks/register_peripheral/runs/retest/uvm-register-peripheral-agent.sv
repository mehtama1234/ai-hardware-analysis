// Generated UVM scaffold; review and compile against the target UVM library.
`include "uvm_macros.svh"
import uvm_pkg::*;

interface registerperipheralagent_if(input logic clk);
  logic clk;
  logic rst;
  logic valid;
  logic write;
  logic addr;
  logic wdata;
  logic ready;
  logic control;
endinterface

class registerperipheralagent_transaction extends uvm_sequence_item;
  `uvm_object_utils(registerperipheralagent_transaction)
  rand logic clk;
  rand logic rst;
  rand logic valid;
  rand logic write;
  rand logic addr;
  rand logic wdata;
  rand logic ready;
  rand logic control;
  function new(string name="registerperipheralagent_transaction"); super.new(name); endfunction
endclass

class registerperipheralagent_agent extends uvm_agent;
  `uvm_component_utils(registerperipheralagent_agent)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

// Dependency order: interface -> transaction -> driver/monitor -> agent -> scoreboard -> env.
class registerperipheralagent_driver extends uvm_driver #(registerperipheralagent_transaction);
  `uvm_component_utils(registerperipheralagent_driver)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class registerperipheralagent_monitor extends uvm_monitor;
  `uvm_component_utils(registerperipheralagent_monitor)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class registerperipheralagent_scoreboard extends uvm_scoreboard;
  `uvm_component_utils(registerperipheralagent_scoreboard)
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass

class registerperipheralagent_env extends uvm_env;
  `uvm_component_utils(registerperipheralagent_env)
  registerperipheralagent_agent agent;
  registerperipheralagent_scoreboard scoreboard;
  function new(string name, uvm_component parent); super.new(name, parent); endfunction
endclass
