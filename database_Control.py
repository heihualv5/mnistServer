import time
from cassandra.cluster import Cluster
def database_ini():
    cluster = Cluster(["0.0.0.0"])
    session = cluster.connect()
    keyspacename='mnist'
    session.execute("create keyspace if not exists mnist with replication = {'class': 'SimpleStrategy', 'replication_factor': 1};")
    session.set_keyspace('mnist')
    session.execute("create table if not exists picdatabase(timestamp double, filedata blob ,answer int ,primary key(timestamp));")
    return session
def database_insert(session,file,pre):
    times=time.time()
    params=[times,bytearray(file),int(pre)]
    session.execute("INSERT INTO picdatabase (timestamp,filedata,answer) VALUES (%s, %s,%s)",params)
    result=session.execute("SELECT * FROM picdatabase")
    for x in result:
        print (x.timestamp,x.filedata,x.answer)
    return 0