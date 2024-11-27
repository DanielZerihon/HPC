// export file declare jenkins pipeline environment variables

// slurm env vars
env.scriptPath='mainBashScript.sh'
env.slurmUser='root'
env.slurmCorrentVersion='v0.0.40'
env.slurmPort='6820'

// elastic env vars
env.elasticUser='elastic'
env.elasticPort='9200'
env.elasticNewIndexName='month-test'

if (System.getenv('HOSTNAME').contains('stageEnv')) {
    env.nodeWorkingDir='/nfsshare'
    env.slurmIP='192.168.100.214'
    env.elasticIP='192.168.100.234'
}
