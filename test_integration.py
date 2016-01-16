import time
import pandas as pd
from integration import Emulation
from traffic_emulator import TrafficEmulator
from traffic_server import TrafficServer
from controller import DummyController

pd.set_option('mode.chained_assignment', None)

# Setting up data
session_df = pd.read_csv(filepath_or_buffer='./data/net_traffic_nonull_sample.dat', sep=',', names=['uid','location','startTime_unix','duration_ms','domainProviders','domainTypes','domains','bytesByDomain','requestsByDomain'])
session_df.index.name = 'sessionID'
session_df['endTime_unix'] = session_df['startTime_unix'] + session_df['duration_ms']
session_df['startTime_datetime'] = pd.to_datetime(session_df['startTime_unix'], unit='ms')  # convert start time to readible date_time strings
session_df['endTime_datetime'] = pd.to_datetime(session_df['endTime_unix'], unit='ms')
session_df['totalBytes'] = session_df['bytesByDomain'].apply(lambda x: x.split(';')).map(lambda x: sum(map(float, x)))  # sum bytes across domains
session_df['totalRequests'] = session_df['requestsByDomain'].apply(lambda x: x.split(';')).map(lambda x: sum(map(float, x)))  # sum requests across domains
session_df.sort(['startTime_datetime'], ascending=True, inplace=True)  # get it sorted
session_df['interArrivalDuration_datetime'] = session_df.groupby('location')['startTime_datetime'].diff()  # group-wise diff
session_df['interArrivalDuration_ms'] = session_df.groupby('location')['startTime_unix'].diff()  # group-wise diff

# Setting up Emulation
te = TrafficEmulator(session_df=session_df, time_step=pd.Timedelta(minutes=1))
ts = TrafficServer()
c = DummyController()
emu = Emulation(te=te, ts=ts, c=c)

# run...
while emu.epoch is not None:
    t = time.time()
    print time.time() - t,
    print "    ",
    print emu.step()

