module traditional_mac 
#(
    parameter WORD_SIZE = 16
)(
    clk,
    rst,
    
    //Control Signals
    fsm_op2_select_in,
    fsm_out_select_in,
    stat_bit_in,        // Drives selects for WS and IS modes

    // Data ports
    left_in,
    top_in, 
    right_out,
    bottom_out
);


input clk;
input rst;

input fsm_op2_select_in;
input fsm_out_select_in;
input stat_bit_in;

input [WORD_SIZE - 1: 0] left_in;
input [WORD_SIZE - 1: 0] top_in;

output [WORD_SIZE - 1: 0] right_out;
output [WORD_SIZE - 1: 0] bottom_out;

wire [255:0] tie_low;

reg [WORD_SIZE - 1: 0] stationary_operand_reg;
reg [WORD_SIZE - 1: 0] top_in_reg;
reg [WORD_SIZE - 1: 0] left_in_reg;
reg [WORD_SIZE - 1: 0] accumulator_reg;

wire [WORD_SIZE - 1: 0] multiplier_out;
wire [WORD_SIZE - 1: 0] adder_out; 
wire [WORD_SIZE - 1: 0] mult_op2_mux_out;
wire [WORD_SIZE - 1: 0] add_op2_mux_out;

assign right_out = left_in_reg;
assign bottom_out = (fsm_out_select_in == 1'b0) ? {tie_low[WORD_SIZE - 1: 0] | top_in_reg} : accumulator_reg;

assign multiplier_out = left_in_reg * mult_op2_mux_out;
assign adder_out = multiplier_out + add_op2_mux_out;

assign mult_op2_mux_out = (stat_bit_in == 1'b1) ? stationary_operand_reg : top_in_reg;
assign add_op2_mux_out = (stat_bit_in == 1'b1) ? top_in_reg : accumulator_reg;

always @(posedge clk, posedge rst)
begin
     if(rst == 1'b1)
     begin
         top_in_reg <= tie_low[WORD_SIZE - 1: 0]; 
         left_in_reg <= tie_low[WORD_SIZE - 1: 0]; 
     end
     else
     begin 
        left_in_reg <= left_in;
        top_in_reg <= top_in;
     end
end

always @(posedge clk, posedge rst)
begin
    if(rst == 1'b1)
    begin
        accumulator_reg <= tie_low [WORD_SIZE - 1: 0]; 
        stationary_operand_reg <= tie_low [WORD_SIZE - 1: 0]; 
    end
    else
    begin
        if (fsm_op2_select_in == 1'b1)
        begin
            stationary_operand_reg <= top_in;
        end

        accumulator_reg <= adder_out;
    end
end

endmodule
