//`include "./traditional_mac.v"

module traditional_systolic_array
#(
    parameter ROWS = 32,
    parameter COLS = 32,
    parameter WORD_SIZE = 16

) (
    clk,
    rst,

    ctl_stat_bit_in, 
    ctl_dummy_fsm_op2_select_in,
    ctl_dummy_fsm_out_select_in,

    left_in_bus,
    top_in_bus,
    bottom_out_bus,
    right_out_bus
);

input clk;
input rst;

input [ROWS * WORD_SIZE - 1: 0] left_in_bus;
input [COLS * WORD_SIZE - 1: 0] top_in_bus;
output [COLS * WORD_SIZE - 1: 0] bottom_out_bus;
output [ROWS * WORD_SIZE - 1: 0] right_out_bus;

input ctl_stat_bit_in; 
input ctl_dummy_fsm_op2_select_in;
input ctl_dummy_fsm_out_select_in;

wire [ROWS * COLS * WORD_SIZE - 1: 0] hor_interconnect;
wire [COLS * ROWS * WORD_SIZE - 1: 0] ver_interconnect;
genvar r, c;

generate
for (r = 0; r < ROWS; r = r + 1)
begin
    assign right_out_bus[(r+1) * WORD_SIZE - 1 -: WORD_SIZE] = hor_interconnect[r * COLS * WORD_SIZE + COLS * WORD_SIZE - 1 -: WORD_SIZE];
end 

for (c  = 0; c < COLS; c = c + 1)
begin
    assign bottom_out_bus[(c+1) * WORD_SIZE - 1 -: WORD_SIZE] = ver_interconnect[(ROWS - 1) * COLS * WORD_SIZE + (c+1) * WORD_SIZE - 1 -: WORD_SIZE];
end

for(r = 0; r < ROWS; r = r+1)
begin
    for(c = 0; c < COLS; c = c+1)
    begin

        localparam VERTICAL_SIGNAL_OFFSET = (c * ROWS + (r+1)) * WORD_SIZE;
        localparam HORIZONTAL_SIGNAL_OFFSET = (r * COLS + (c+1)) * WORD_SIZE;

        if ((r == 0) && (c==0))
        begin

            traditional_mac #(
                .WORD_SIZE(WORD_SIZE)
            ) u_mac_top_left(
                .clk(clk),
                .rst(rst),
                .fsm_op2_select_in(ctl_dummy_fsm_op2_select_in),
                .fsm_out_select_in(ctl_dummy_fsm_out_select_in),
                .stat_bit_in(ctl_stat_bit_in),
                .left_in(left_in_bus[(r+1) * WORD_SIZE -1 -: WORD_SIZE]),
                .top_in(top_in_bus[(c+1) * WORD_SIZE - 1 -: WORD_SIZE]),
                .right_out(hor_interconnect[VERTICAL_SIGNAL_OFFSET - 1 -: WORD_SIZE]),
                .bottom_out(ver_interconnect[HORIZONTAL_SIGNAL_OFFSET -1 -: WORD_SIZE])
            );
        end
        else if (c==0)
        begin

            localparam TOP_PEER_OFFSET = ((r - 1) * COLS + (c+1)) * WORD_SIZE;

            traditional_mac #(
                .WORD_SIZE(WORD_SIZE)
            ) u_mac_left_col(
                .clk(clk),
                .rst(rst),
                .fsm_op2_select_in(ctl_dummy_fsm_op2_select_in),
                .fsm_out_select_in(ctl_dummy_fsm_out_select_in),
                .stat_bit_in(ctl_stat_bit_in),
                .left_in(left_in_bus[(r+1) * WORD_SIZE -1 -: WORD_SIZE]),
                .top_in(ver_interconnect[TOP_PEER_OFFSET -1 -: WORD_SIZE]),
                .right_out(hor_interconnect[VERTICAL_SIGNAL_OFFSET -1 -: WORD_SIZE]),
                .bottom_out(ver_interconnect[HORIZONTAL_SIGNAL_OFFSET -1 -: WORD_SIZE])
            );
        end
        else if (r==0)
        begin

            localparam LEFT_PEER_OFFSET = (r * COLS + c) * WORD_SIZE;

            traditional_mac #(
                .WORD_SIZE(WORD_SIZE)
            ) u_mac_top_row(
                .clk(clk),
                .rst(rst),
                .fsm_op2_select_in(ctl_dummy_fsm_op2_select_in),
                .fsm_out_select_in(ctl_dummy_fsm_out_select_in),
                .stat_bit_in(ctl_stat_bit_in),
                .left_in(hor_interconnect[LEFT_PEER_OFFSET - 1 -: WORD_SIZE]),
                .top_in(top_in_bus[(c+1) * WORD_SIZE - 1 -: WORD_SIZE]),
                .right_out(hor_interconnect[VERTICAL_SIGNAL_OFFSET -1 -: WORD_SIZE]),
                .bottom_out(ver_interconnect[HORIZONTAL_SIGNAL_OFFSET -1 -: WORD_SIZE])
            );
        end
        else
        begin

            localparam TOP_PEER_OFFSET = ((r - 1) * COLS + (c+1)) * WORD_SIZE;
            localparam LEFT_PEER_OFFSET = (r * COLS + c) * WORD_SIZE;
            
            traditional_mac #(
                .WORD_SIZE(WORD_SIZE)
            ) u_mac_rest(
                .clk(clk),
                .rst(rst),
                .fsm_op2_select_in(ctl_dummy_fsm_op2_select_in),
                .fsm_out_select_in(ctl_dummy_fsm_out_select_in),
                .stat_bit_in(ctl_stat_bit_in),
                .left_in(hor_interconnect[LEFT_PEER_OFFSET - 1 -: WORD_SIZE]),
                .top_in(ver_interconnect[TOP_PEER_OFFSET -1 -: WORD_SIZE]),
                .right_out(hor_interconnect[VERTICAL_SIGNAL_OFFSET -1 -: WORD_SIZE]),
                .bottom_out(ver_interconnect[HORIZONTAL_SIGNAL_OFFSET -1 -: WORD_SIZE])
            );
        end
    end
end
endgenerate

endmodule
