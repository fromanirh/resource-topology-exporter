module github.com/swatisehgal/resource-topology-exporter

go 1.13

require (
	github.com/davecgh/go-spew v1.1.1
	github.com/docopt/docopt-go v0.0.0-20180111231733-ee0de3bc6815
	github.com/fromanirh/numalign v0.0.3
	github.com/ghodss/yaml v1.0.0
	github.com/golang/protobuf v1.4.2 // indirect
	github.com/googleapis/gnostic v0.3.1 // indirect
	github.com/intel/sriov-network-device-plugin v0.0.0-20200603101849-e116e9c7d0b8
	github.com/json-iterator/go v1.1.10 // indirect
	github.com/opencontainers/runtime-spec v1.0.0
	github.com/swatisehgal/topologyapi v0.0.0-20200701120235-74ecc412df7b
	golang.org/x/net v0.0.0-20200520004742-59133d7f0dd7 // indirect
	golang.org/x/text v0.3.3 // indirect
	google.golang.org/grpc v1.28.1
	gopkg.in/check.v1 v1.0.0-20190902080502-41f04d3bba15 // indirect
	gopkg.in/yaml.v2 v2.3.0 // indirect
	k8s.io/api v0.18.6
	k8s.io/apimachinery v0.18.6
	k8s.io/client-go v0.18.6
	k8s.io/cri-api v0.0.0
	k8s.io/kubelet v0.18.1
	k8s.io/kubernetes v1.18.6
	k8s.io/utils v0.0.0-20200603063816-c1c6865ac451 // indirect
)

// Pinned to kubernetes-1.18.6
replace (
	k8s.io/api => k8s.io/api v0.18.6
	k8s.io/apiextensions-apiserver => k8s.io/apiextensions-apiserver v0.18.6
	k8s.io/apimachinery => k8s.io/apimachinery v0.18.6
	k8s.io/apiserver => k8s.io/apiserver v0.18.6
	k8s.io/cli-runtime => k8s.io/cli-runtime v0.18.6
	k8s.io/client-go => k8s.io/client-go v0.18.6
	k8s.io/cloud-provider => k8s.io/cloud-provider v0.18.6
	k8s.io/cluster-bootstrap => k8s.io/cluster-bootstrap v0.18.6
	k8s.io/code-generator => k8s.io/code-generator v0.18.6
	k8s.io/component-base => k8s.io/component-base v0.18.6
	k8s.io/cri-api => k8s.io/cri-api v0.18.6
	k8s.io/csi-translation-lib => k8s.io/csi-translation-lib v0.18.6
	k8s.io/kube-aggregator => k8s.io/kube-aggregator v0.18.6
	k8s.io/kube-controller-manager => k8s.io/kube-controller-manager v0.18.6
	k8s.io/kube-proxy => k8s.io/kube-proxy v0.18.6
	k8s.io/kube-scheduler => k8s.io/kube-scheduler v0.18.6
	k8s.io/kubectl => k8s.io/kubectl v0.18.6
	k8s.io/kubelet => k8s.io/kubelet v0.18.6
	k8s.io/kubernetes => k8s.io/kubernetes v1.18.6
	k8s.io/legacy-cloud-providers => k8s.io/legacy-cloud-providers v0.18.6
	k8s.io/metrics => k8s.io/metrics v0.18.6
	k8s.io/sample-apiserver => k8s.io/sample-apiserver v0.18.6
	sigs.k8s.io/controller-runtime => sigs.k8s.io/controller-runtime v0.5.7
)
