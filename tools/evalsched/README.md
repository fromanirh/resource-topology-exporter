# evalsched - scheduler behaviour exploration tool

evalsched is a little helper to allow us explore the implicationions and the interplay between
the resource topology exporter update period and the topology-aware scheduler behaviour.
Due to its simplistic nature, is *not* meant to provide definitive answers, which can only be
provided by actual testing, but rather as initial exploration tool, to actually drive the experiments.

## key assumptions

A number of assumptions characterize the `evalsched` model:
- we focus on the information propagation delay between node and scheduler. All the timing components (e.g. rte period,
  apiserver/etcd delays, network delays) are coalesced in a single value.
- the propagation delay is constant, and constant for all nodes - even though node have a random initial delay.
- once properly informed (= feed with up to date information) the scheduler makes the right call.
- the only reason why the scheduler may fail is the lack of timely updates from nodes.
- we don't care about the actual scheduling decision, so we model it as random choice.
- we coalesce all possible scheduling error in a single error due to lack of updates.

## running evalsched

`evalsched` takes at least two arguments: the first is the `config.json` which sets the simulation environment:
how the cluster looks like. The second (and any other following) represent the pod creation pattern.

## config.json: the cluster model

```json
{
	"nodes": {
		"number": 2,
		"capacity": 100,
		"update_period_seconds": 3
	}
}
```

`nodes`: configure the cluster, as follows
* `number`: how many *WORKER* nodes the cluster will have. Worker nodes will be used to schedule simulated pods
* `capacity`: how many pods *each* node can hold. You usually want to make sure that `number * capacity < pods` you want to schedule.
* `update_period_seconds`: simulate RTE polling interval. Set to `0` to make simulated RTE report the updated node capacity after
   *each* node state change (pod admission/deletion)


## pod creation distribution model
TBD

## evaluating results
TBD

