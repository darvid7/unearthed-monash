"""
@author: David Lei
@since: 18/03/2017
@modified: 

"""
class GenericPasrer:

    def __init__(self, pi, fail, csv_data_dir):
        self.performance_indicator_data = pi
        self.failure_data = fail
        self.csv_data_dir = csv_data_dir

    def parse_perf_indicator_csv(self, filename):
        with open(os.path.join(self.csv_data_dir, filename), 'r') as csv_file:
            csv_data = csv_file.readlines()
            parsed_csv_data = CsvSheetParser(csv_data)

            """
            timestamp,3212SI005A.PV,3212SI205A.PV,3212SI405A.PV,3212SI605A.PV,3212SI805A.PV,3234LIT001.PV,3234LIT072.PV,3234LIT181.PV,3234SY055.PV,3235SY015.PV,3235WIT051.PV,3235WQS051.PV,3244SY055.PV,3244SY1055.PV,3245WIT051.PV,3245WIT1051.PV,CR30011PPVI.PV,CR30211PPVI.PV,CR30221PPVI.PV,CV3011SW.PV,CV3033_PWRCONSUM.PV,CV3033_RUNNING.PV,CV3033_TWT.PV,CV3101SW.PV,FD3001_SPD.PV,FD3001SPD_NOM.PV,FD3011P.PV,FD3011SPD_PID.SV,FD3011SW.PV,MD3001MTL.PV,RB3001SW.PV,VS3033SW.PV,3212LI1165.PV,CV002TNS.PV,SY21633A.MV,SY21633B.MV,SY21633C.MV,WI21633A.PV,ZY21653C.PV,3311JI017.PV,3311LI066.PV,3311LI300.PV,3311VI012.PV,3311WDI671.PV,3311WI672.PV,3311WIC151.MV,
            """

