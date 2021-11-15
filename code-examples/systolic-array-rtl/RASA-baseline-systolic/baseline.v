module baseline #(
	parameter ADD_BW = 32, // note parameters are kinda set for this desgin due to fixed multipler & adder units
	parameter MUL_BW = 16) (
	input clk,
	input rst,
	input i_mode,
	input [ADD_BW-1:0] i_top,
	input [MUL_BW-1:0] i_left,
	output reg [ADD_BW-1:0] o_bot,
	output reg [MUL_BW-1:0] o_right
);

	reg [MUL_BW-1:0] r_buffer; // weight register
	wire [MUL_BW-1:0] w_mult_out;
	
	wire [ADD_BW-1:0] w_adder_in;
	wire [ADD_BW-1:0] w_adder_out;
	
	wire [ADD_BW-1:0] w_out;
	
	// set weight buffer when i_mode = 0 (load)
	always @ (*) begin
		if (rst == 1'b1) begin
			r_buffer = 'd0;
		end else begin
			if (i_mode == 1'b0) begin
				r_buffer = i_top[MUL_BW-1:0];
			end
		end
	end
	
	// set adder in when i_mode = 1 (accum), else set to zero
	assign w_adder_in = i_mode ? i_top : 'd0;
	
	
	bfp16_mult mult1(
		.clk(clk),
		.rst(rst),
		.A(i_left),
		.B(r_buffer),
		.O(w_mult_out)
	);
	
	bfp32_adder adder1(
		.clk(clk),
		.rst(rst),
		.A(w_adder_in),
		.B({w_mult_out, 16'b0}),
		.O(w_adder_out)
	);
	
	// assign output wire to either w_adder_out or 16:0 for loading data
	assign w_out = i_mode ? w_adder_out: {16'b0, i_top[MUL_BW-1:0]};
	
	// flop outputs
	always @ (posedge clk or negedge rst) begin
		if (rst == 1'b0) begin
			o_bot <= 'd0;
			o_right <= 'd0;
		end else begin
			o_bot <= w_out;
			o_right <= i_left;
		end
	end
	

endmodule