import pandas as pd


class ScalesimReport:
    def __init__(self):
        self.compute_df = pd.DataFrame()
        self.bandwidths_df = pd.DataFrame()
        self.details_df = pd.DataFrame()

        self.compute_df_ready = False
        self.bandwidths_df_ready = False
        self.details_df_ready = False

    #
    def load_data(self, data_dir='.', run_name=''):
        self.load_compute_report_data(data_dir=data_dir, run_name=run_name)
        self.load_bandwidth_report_data(data_dir=data_dir, run_name=run_name)
        self.load_detail_report_data(data_dir=data_dir, run_name=run_name)

    #
    def load_compute_report_data(self, data_dir='.', run_name=''):
        csv_filename = data_dir + '/' + run_name + '/COMPUTE_REPORT.csv'
        self.compute_df = pd.read_csv(csv_filename, sep=r'\s*,\s*', engine='python')
        self.compute_df_ready = True

    #
    def load_bandwidth_report_data(self, data_dir='.', run_name=''):
        csv_filename = data_dir + '/' + run_name + '/BANDWIDTH_REPORT.csv'
        self.bandwidths_df = pd.read_csv(csv_filename, sep=r'\s*,\s*', engine='python')
        self.bandwidths_df_ready = True

    #
    def load_detail_report_data(self, data_dir='.', run_name=''):
        csv_filename = data_dir + '/' + run_name + '/DETAILED_ACCESS_REPORT.csv'
        self.bandwidths_df = pd.read_csv(csv_filename, sep=r'\s*,\s*', engine='python')
        self.details_df_ready = True

    #
    def get_total_cycles_single_layer(self, layer_id=0):
        assert self.compute_df_ready, 'Data not read yet'
        col_name = 'Total Cycles'
        elem = self.compute_df[col_name][layer_id]

        return elem

    #
    def get_compute_cycles_all_layer(self):
        assert self.compute_df_ready, 'Data not read yet'
        col_name = 'Total Cycles'
        elems = self.compute_df[col_name].to_list()

        return elems

    #
    def get_sram_ifmap_reads_single_layer(self, layer_id=0):
        assert self.details_df_ready, 'Data not read yet'
        col_name = 'SRAM IFMAP Reads'
        elem = self.details_df[col_name][layer_id]

        return elem

    #
    def get_sram_ifmap_reads_all_layer(self):
        assert self.details_df_ready, 'Data not read yet'
        col_name = 'SRAM IFMAP Reads'
        elems = self.details_df[col_name].to_list()

        return elems

if __name__ == '__main__':
    rpt = ScalesimReport()
    rpt.load_data(data_dir='./tutorial1_runs', run_name='scale_sim_tutorial1_64x64_os')

    print(rpt.get_compute_cycles_all_layer())
    print(rpt.get_total_cycles_single_layer(layer_id=1))
