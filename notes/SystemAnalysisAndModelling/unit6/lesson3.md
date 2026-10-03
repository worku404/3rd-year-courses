# Lesson 3 — Component & Deployment Diagrams: Physical Architecture & Distributed Topology

## Executive Summary & Academic Orientation

In enterprise-scale software engineering, bridging the chasm between logical class hierarchies and real-world execution environments is an architectural imperative. While class and object diagrams model software abstractions residing in volatile memory, **Component Diagrams** and **Deployment Diagrams** model the physical, deployable, and operational realities of complex distributed systems.

According to the **UML 2.5 Specification**, components represent modular, encapsulated units of functionality with cleanly decoupled boundaries. They express system capabilities exclusively through formal contracts: **Provided Interfaces** (the services a component offers) and **Required Interfaces** (the services a component demands).

Complementing this modular view, **Deployment Diagrams** capture the physical hardware execution topology—mapping executable artifacts (`.jar`, `.so`, Docker container images) onto hardware execution nodes (physical servers, virtual machines, cloud instances) and execution environment nodes (EENs such as JVMs, Kubernetes pods, or database engines).

```
+-------------------------------------------------------------------------+
|                  UML 2.5 COMPONENT-TO-DEPLOYMENT CONTINUUM              |
|                                                                         |
|  [ Logical Abstraction ]         [ Deployable Unit ]                    |
|    Classes & Packages     --->     <<component>> AuthModule             |
|                                      (Provided: IAuth, Required: IDB)   |
|                                           |                             |
|                                     Packaged Into                       |
|                                           v                             |
|                                    <<artifact>> auth_service.jar        |
|                                           |                             |
|                                     Deployed Onto                       |
|                                           v                             |
|  [ Execution Environment ]         <<executionEnvironment>>             |
|                                    Docker / OpenJDK 17 Container        |
|                                           |                             |
|                                     Hosted Within                       |
|                                           v                             |
|  [ Physical Infrastructure ]       <<device>> Bare-Metal Blade Server   |
|                                    (Dual Xeon, 128GB RAM, 10Gbps NIC)   |
+-------------------------------------------------------------------------+
```

---

## 3.1 Component Diagrams: Autonomous Modularity and Interface Assembly

### Metamodel Definition of a Component

In the UML 2.5 metamodel, a `Component` is a specialized structured classifier that defines autonomous, replaceable units within a system. A component encapsulates its private internal implementation details behind rigorous public boundaries.

```
+-------------------------------------------------------------------------+
|                 BALL-AND-SOCKET (LOLLIPOP) NOTATION                      |
|                                                                         |
|   +--------------------+                         +--------------------+ |
|   |   <<component>>    |                         |   <<component>>    | |
|   |  OrderProcessor    |----(  IOrderService  )----|   BillingEngine    | |
|   +--------------------+   Ball             Socket+--------------------+ |
|                         (Provided)        (Required)                    |
|                                                                         |
|   - Ball (Lollipop):  Provided Interface (Offers capability to peers)   |
|   - Socket (Cup):     Required Interface (Demands capability from peer) |
+-------------------------------------------------------------------------+
```

### The Provided and Required Interface Duality

1. **Provided Interface ($\mathcal{I}_P$) — Ball / Lollipop**:
   - Represents the formal contract of operations, signals, and semantic guarantees that the component fulfills for its clients.
   - Notation: A solid line terminating in a complete circle labeled with the interface name (e.g., `—( IPaymentGateway )`).
2. **Required Interface ($\mathcal{I}_R$) — Socket / Cup**:
   - Represents the set of external dependencies and interfaces that the component necessitates to perform its internal logic.
   - Notation: A solid line terminating in a half-circle or concave cup facing the interface provider (e.g., `—) IAuditLogger (—`).
3. **Assembly Connector**:
   - When a component offering $\mathcal{I}_P$ is directly wired to a component demanding $\mathcal{I}_R$, the ball fits into the socket.
   - Formal Requirement: The provided interface must be a structural subtype or exact match of the required interface:
     $$\mathcal{I}_P \sqsupseteq \mathcal{I}_R$$

---

## 3.2 Explicit Component Boundary Ports, Wiring Connectors, and Subsystem Packaging

### Ports (`UML::CompositeStructures::Port`)

In large-scale microservice architectures, components must not leak internal wiring. UML provides **Ports**—distinct interaction points on the component boundary through which all incoming and outgoing messages must pass.

```
+-------------------------------------------------------------------------+
|                INTERNAL COMPONENT STRUCTURE & PORTS                     |
|                                                                         |
|  +-------------------------------------------------------------------+  |
|  | <<component>>                                                     |  |
|  | TradingGateway                                                    |  |
|  |                                                                   |  |
|  |    [p1:Port]--( IOrderEntry )       [p2:Port]--) IMarketFeed      |  |
|  |        |                                 |                        |  |
|  |    Delegation Connector              Delegation Connector         |  |
|  |        |                                 |                        |  |
|  |        v                                 v                        |  |
|  |   +---------------+                 +---------------+             |  |
|  |   | OrderValidator|                 | PricingEngine |             |  |
|  |   +---------------+                 +---------------+             |  |
|  |          |                                 |                      |  |
|  |          +-------- Assembly Connector -----+                      |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

### Delegation vs. Assembly Connectors
- **Delegation Connector**: Connects an external boundary port to an internal classifier/class that realizes the interface. It translates external boundary invocations into internal method dispatches without exposing internal topologies.
- **Assembly Connector**: Connects two internal parts/components directly within a composite structured classifier.

---

## Visual Architecture: Component Wiring & Deployment Topology

{{ media:sam-component-deployment-diagram }}

### Multimedia Deep-Dive: Distributed System Topologies & Deployment
Examine real-world distributed architectures, container boundaries, and cloud deployment topology design:

{{ media:component-deployment-video }}

---

## 3.3 Deployment Diagrams: Physical Nodes vs. Execution Environment Nodes (EENs)

```
+-------------------------------------------------------------------------+
|                  UML 2.5 NODE TAXONOMY & CLOUD TOPOLOGY                 |
|                                                                         |
|  <<device>>                                                             |
|  +-------------------------------------------------------------------+  |
|  | AWS EC2 Bare-Metal Host: i3en.metal                               |  |
|  |                                                                   |  |
|  |   <<executionEnvironment>>                                        |  |
|  |   +-----------------------------------------------------------+   |  |
|  |   | Containerd Runtime / Kubelet Engine                       |   |  |
|  |   |                                                           |   |  |
|  |   |   <<executionEnvironment>>                                |   |  |
|  |   |   +---------------------------------------------------+   |   |  |
|  |   |   | Pod: order-processor-deployment-7f99b             |   |   |  |
|  |   |   |                                                   |   |   |  |
|  |   |   |   <<artifact>>                                    |   |   |  |
|  |   |   |   +-------------------------------------------+   |   |   |  |
|  |   |   |   | order_service_v2.jar                      |   |   |   |  |
|  |   |   |   +-------------------------------------------+   |   |   |  |
|  |   |   +---------------------------------------------------+   |   |  |
|  |   +-----------------------------------------------------------+   |  |
|  +-------------------------------------------------------------------+  |
+-------------------------------------------------------------------------+
```

### Nodes Metamodel Classification

In UML 2.5, a **Node** represents computational resource hardware or execution infrastructure. Nodes are rendered graphically as **3D Cubes (parallelopipeds)**.

1. **Device Node (`<<device>>`)**:
   - Represents physical computational hardware with processing capability, memory, and physical I/O peripherals.
   - Examples: `<<device>> ApplicationServerBlade`, `<<device>> CiscoCoreRouter`, `<<device>> IoTEdgeSensor`.
2. **Execution Environment Node (`<<executionEnvironment>>` or `EEN`)**:
   - Represents a software platform or runtime engine that executes other executable artifacts.
   - Examples: `<<executionEnvironment>> JVM 21`, `<<executionEnvironment>> Node.js v20`, `<<executionEnvironment>> PostgreSQL 16 Cluster`.
3. **Nested Nodes**:
   - An EEN can be nested within a Device Node to model hypervisors, container engines, or guest virtual machines residing inside physical server hardware.

---

## 3.4 Software Artifacts, Deployment Manifests, and Communication Paths

### Artifacts (`<<artifact>>`)
An **Artifact** represents physical packaged information produced by the software engineering development process:
- Executable binaries: `trading_engine.exe`, `api_gateway.bin`
- Package archives: `payment_service.jar`, `dist.tar.gz`
- Docker container images: `redis:7.2-alpine`
- Configuration schemas: `application.yaml`, `cert.pem`

Notation: A rectangular classifier box with the keyword `<<artifact>>` or a document icon with a folded top-right corner.

### Deployment Relationships
- **`<<deploy>>` Dependency**: Directed dashed arrow from an `<<artifact>>` to the `Node` where it is physically hosted.
- **Direct Nesting**: Rendering the artifact rectangle directly inside the 3D volume of the node cube.

### Communication Paths (`<<communication path>>`)
Solid undirected or directed lines connecting two distinct physical nodes:
- Must specify the physical or logical network protocol stereotype:
  - `«gRPC / HTTP/2»`
  - `«TLS 1.3 / TCP:443»`
  - `«AMQP / RabbitMQ»`
  - `«NVMe-oF / RoCEv2»` (RDMA over Converged Ethernet)

---

## 3.5 Mapping Logical Microservice Containers to Cloud Regions

When designing distributed enterprise systems (e.g., in AWS, Azure, or GCP), the architect must specify geographical redundancy and failure boundaries.

```
+-------------------------------------------------------------------------+
|                  MULTI-REGION DISASTER RECOVERY TOPOLOGY                |
|                                                                         |
|  Region us-east-1 (Primary):           Region us-west-2 (Standby):      |
|  +---------------------------+         +---------------------------+    |
|  | <<device>>                |         | <<device>>                |    |
|  | Cloud Cluster Node        |         | Cloud Cluster Node        |    |
|  |   [API Gateway]           |         |   [API Gateway]           |    |
|  |         |                 |         |         |                 |    |
|  |   [Order Service]         |         |   [Order Service]         |    |
|  |         |                 |         |         |                 |    |
|  |   [PostgreSQL Primary]    |====(Cross-Region Replication)====>       |
|  |                           |         |   [PostgreSQL Replica]    |    |
|  +---------------------------+         +---------------------------+    |
+-------------------------------------------------------------------------+
```

---

## 3.6 Component Interface Wiring & Distributed Topology Engine in C++17

The following industrial C++17 simulation engine implements a formal component assembly and physical deployment validator. It models provided/required interfaces, verifies signature compatibility, detects mismatched boundary ports, and simulates cross-node network latency across distributed communication paths.

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <memory>
#include <stdexcept>
#include <iomanip>

// ============================================================================
// COMPONENT METAMODEL: Interfaces, Ports, and Assemblies
// ============================================================================

struct InterfaceMethod {
    std::string methodName;
    std::string returnType;
    std::vector<std::string> paramTypes;

    bool operator==(const InterfaceMethod& other) const {
        return methodName == other.methodName &&
               returnType == other.returnType &&
               paramTypes == other.paramTypes;
    }
};

struct InterfaceContract {
    std::string interfaceName;
    std::vector<InterfaceMethod> operations;

    // Evaluates if this interface conforms to (fulfills) required contract
    bool satisfies(const InterfaceContract& required) const {
        for (const auto& reqOp : required.operations) {
            bool found = false;
            for (const auto& provOp : operations) {
                if (provOp == reqOp) {
                    found = true;
                    break;
                }
            }
            if (!found) return false;
        }
        return true;
    }
};

struct ComponentPort {
    std::string portName;
    std::string componentOwner;
    std::optional<InterfaceContract> providedInterface;
    std::optional<InterfaceContract> requiredInterface;
};

struct Component {
    std::string componentName;
    std::unordered_map<std::string, ComponentPort> ports;

    void addPort(const ComponentPort& port) {
        ports[port.portName] = port;
    }
};

// ============================================================================
// DEPLOYMENT METAMODEL: Devices, Execution Environments, and Protocols
// ============================================================================

enum class NodeType { PHYSICAL_DEVICE, EXECUTION_ENVIRONMENT };

struct DeploymentNode {
    std::string nodeName;
    NodeType type;
    std::string ipAddress;
    std::unordered_set<std::string> hostedArtifacts;      // Artifact names
    std::vector<std::shared_ptr<DeploymentNode>> subNodes; // Nested EENs
};

struct NetworkLink {
    std::string sourceNode;
    std::string targetNode;
    std::string protocol; // e.g. "gRPC", "HTTPS", "AMQP"
    double latencyMs;
    double bandwidthMbps;
};

// ============================================================================
// ARCHITECTURAL VERIFICATION & SIMULATION ENGINE
// ============================================================================

class ArchitectureTopologyEngine {
private:
    std::unordered_map<std::string, Component> componentRegistry;
    std::unordered_map<std::string, DeploymentNode> nodeRegistry;
    std::unordered_map<std::string, std::string> artifactToComponent; // Artifact -> Component
    std::vector<NetworkLink> networkTopology;

public:
    void registerComponent(const Component& comp) {
        componentRegistry[comp.componentName] = comp;
    }

    void registerNode(const DeploymentNode& node) {
        nodeRegistry[node.nodeName] = node;
    }

    void deployArtifact(const std::string& nodeName, const std::string& artifactName, const std::string& compName) {
        if (nodeRegistry.find(nodeName) == nodeRegistry.end()) {
            throw std::runtime_error("Node not found: " + nodeName);
        }
        nodeRegistry[nodeName].hostedArtifacts.insert(artifactName);
        artifactToComponent[artifactName] = compName;
    }

    void addNetworkPath(const std::string& src, const std::string& tgt, const std::string& proto, double latency, double bw) {
        networkTopology.push_back({src, tgt, proto, latency, bw});
    }

    // Validates Assembly Connector: Checks Ball-and-Socket contract compatibility
    bool validateAssemblyWiring(const std::string& provComp, const std::string& provPort,
                                const std::string& reqComp,  const std::string& reqPort,
                                std::string& outError) const {
        if (componentRegistry.find(provComp) == componentRegistry.end()) {
            outError = "Provider component '" + provComp + "' not registered.";
            return false;
        }
        if (componentRegistry.find(reqComp) == componentRegistry.end()) {
            outError = "Requiring component '" + reqComp + "' not registered.";
            return false;
        }

        const auto& pPort = componentRegistry.at(provComp).ports.at(provPort);
        const auto& rPort = componentRegistry.at(reqComp).ports.at(reqPort);

        if (!pPort.providedInterface.has_value()) {
            outError = "Port " + provPort + " does not expose a Provided Interface.";
            return false;
        }
        if (!rPort.requiredInterface.has_value()) {
            outError = "Port " + reqPort + " does not demand a Required Interface.";
            return false;
        }

        const auto& provIface = pPort.providedInterface.value();
        const auto& reqIface = rPort.requiredInterface.value();

        if (!provIface.satisfies(reqIface)) {
            outError = "Interface Mismatch! Provided '" + provIface.interfaceName +
                       "' does not satisfy contract for Required '" + reqIface.interfaceName + "'.";
            return false;
        }

        return true;
    }

    // Calculates end-to-end communication latency between two communicating components
    double calculateCommunicationLatency(const std::string& compA, const std::string& compB) const {
        // Find which node hosts each component
        std::string nodeA, nodeB;
        for (const auto& [nName, node] : nodeRegistry) {
            for (const auto& art : node.hostedArtifacts) {
                if (artifactToComponent.at(art) == compA) nodeA = nName;
                if (artifactToComponent.at(art) == compB) nodeB = nName;
            }
        }

        if (nodeA.empty() || nodeB.empty()) {
            throw std::runtime_error("Component placement incomplete.");
        }

        if (nodeA == nodeB) {
            return 0.05; // Inter-process memory bus latency (~50 microseconds)
        }

        // Search network path
        for (const auto& link : networkTopology) {
            if ((link.sourceNode == nodeA && link.targetNode == nodeB) ||
                (link.sourceNode == nodeB && link.targetNode == nodeA)) {
                return link.latencyMs;
            }
        }

        return 999999.0; // Unreachable
    }

    void displayDeploymentSummary() const {
        std::cout << "\n====================================================================\n";
        std::cout << "                 PHYSICAL DEPLOYMENT TOPOLOGY REPORT                \n";
        std::cout << "====================================================================\n";
        for (const auto& [nName, node] : nodeRegistry) {
            std::cout << "  Node: [" << (node.type == NodeType::PHYSICAL_DEVICE ? "<<device>> " : "<<EEN>> ")
                      << nName << "] (IP: " << node.ipAddress << ")\n";
            std::cout << "    |-- Hosted Artifacts:\n";
            for (const auto& art : node.hostedArtifacts) {
                std::cout << "        * " << art << " -> [Component: " << artifactToComponent.at(art) << "]\n";
            }
        }
        std::cout << "\n  Network Paths:\n";
        for (const auto& link : networkTopology) {
            std::cout << "    (" << link.sourceNode << ") <---[ " << link.protocol 
                      << " | Latency: " << link.latencyMs << " ms | BW: " << link.bandwidthMbps << " Mbps ]---> (" 
                      << link.targetNode << ")\n";
        }
        std::cout << "====================================================================\n";
    }
};

int main() {
    ArchitectureTopologyEngine engine;

    // 1. Define Interface Contracts
    InterfaceContract iOrderService{
        "IOrderService",
        {
            {"submitOrder", "bool", {"string", "double"}},
            {"cancelOrder", "bool", {"string"}}
        }
    };

    // 2. Define Components & Ports
    Component orderComp{"OrderServiceComponent", {}};
    orderComp.addPort({"pOrders", "OrderServiceComponent", iOrderService, std::nullopt});

    Component clientComp{"WebStorefrontComponent", {}};
    clientComp.addPort({"pCheckout", "WebStorefrontComponent", std::nullopt, iOrderService});

    engine.registerComponent(orderComp);
    engine.registerComponent(clientComp);

    // 3. Verify Assembly Wiring
    std::string error;
    bool wired = engine.validateAssemblyWiring("OrderServiceComponent", "pOrders",
                                               "WebStorefrontComponent", "pCheckout", error);
    std::cout << "Assembly Connector Check: " << (wired ? "SUCCESS (Contracts Matched)" : "FAILED: " + error) << "\n";

    // 4. Model Deployment Topology
    DeploymentNode webNode{"WebFrontHost_01", NodeType::PHYSICAL_DEVICE, "10.0.1.10", {}, {}};
    DeploymentNode appNode{"AppClusterNode_01", NodeType::PHYSICAL_DEVICE, "10.0.2.20", {}, {}};

    engine.registerNode(webNode);
    engine.registerNode(appNode);

    engine.deployArtifact("WebFrontHost_01", "storefront_v1.war", "WebStorefrontComponent");
    engine.deployArtifact("AppClusterNode_01", "order_service_v2.jar", "OrderServiceComponent");

    engine.addNetworkPath("WebFrontHost_01", "AppClusterNode_01", "gRPC over HTTP/2 (mTLS)", 1.25, 10000.0);

    engine.displayDeploymentSummary();

    double latency = engine.calculateCommunicationLatency("WebStorefrontComponent", "OrderServiceComponent");
    std::cout << "Estimated Cross-Component Invocation Latency: " << latency << " ms\n";

    return 0;
}
```

---

## 3-Tier Progressive Practice Suite

### Level 1: Guided Architectural Walkthrough & Step-by-Step Analysis

#### Problem Statement
An enterprise banking core models an authorization component:
- Component: `AuthorizationService`
  - Port `authIn`: Provides `IAuthenticator` (`authenticateUser(user, pass): Token`, `verifyToken(Token): bool`)
  - Port `auditOut`: Demands `IAuditLog` (`recordEvent(level, msg): void`)
- Component: `AuditService`
  - Port `logIn`: Provides `ISimpleLog` (`recordEvent(level, msg): void`)
- Component: `BankingPortal`
  - Port `authClient`: Demands `IAuthenticator` (`authenticateUser(user, pass): Token`)

#### Architectural Analysis Questions
1. Can an assembly connector legally join `BankingPortal::authClient` to `AuthorizationService::authIn`?
2. Can an assembly connector legally join `AuthorizationService::auditOut` to `AuditService::logIn` even though the interface type names differ (`IAuditLog` vs. `ISimpleLog`)?

#### Guided Solution
1. **Analysis of `authClient` to `authIn`**:
   - `BankingPortal` demands an interface with one method (`authenticateUser`).
   - `AuthorizationService` provides an interface with two methods (`authenticateUser` and `verifyToken`).
   - By the Liskov Substitution and Subtyping Principle ($\mathcal{I}_P \sqsupseteq \mathcal{I}_R$), the provider fulfills all operations demanded by the client. The assembly connector is **valid**.
2. **Analysis of `auditOut` to `logIn`**:
   - Under nominal typing in UML, interfaces must share the same classifier identity unless an explicit structural mapping, adapter stereotype, or realization relationship is defined.
   - However, in structural subtyping, since both define the identical signature `recordEvent(level, msg): void`, an **Adapter Component** or formal UML `<<realizes>>` generalization must be declared in the model to bridge the naming discrepancy.

---

### Level 2: Scaffolded Troubleshooting / Bug-Fix Challenge

#### Challenge Description
A junior devops architect submits the following deployment diagram fragment for a HIPAA-compliant medical records platform:

```
  <<device>> ClientMobilePhone
  +-------------------------------------+
  | <<artifact>> patient_app.apk        |
  +-------------------------------------+
                     |
                     |  «HTTP / Insecure Plaintext»
                     v
  <<device>> CloudLoadBalancer (Public IP: 198.51.100.1)
  +-------------------------------------+
                     |
                     |  «TCP:8080»
                     v
  <<executionEnvironment>> DockerContainer
  +-------------------------------------+
  | <<artifact>> medical_records_api.jar|
  +-------------------------------------+
                     |
                     |  Direct Physical Cable ?
                     v
  <<device>> OnPremisesHospitalDatabase (Private IP: 192.168.1.50)
```

Identify the three severe architectural and modeling defects in this deployment diagram.

<details>
<summary>Click to view solution & walkthrough</summary>

#### Diagnostic Breakdown

1. **Security & Compliance Invariant Violation (Plaintext Protocol)**:
   - *Defect*: The communication path from `ClientMobilePhone` across the public internet to `CloudLoadBalancer` is stereotyped as `«HTTP / Insecure Plaintext»`.
   - *Hazard*: Violates HIPAA, GDPR, and basic cyber-security requirements.
   - *Fix*: Stereotype must be updated to `«TLS 1.3 / HTTPS / Port:443»`.

2. **Metamodel Structural Defect (Unparented Execution Environment)**:
   - *Defect*: `<<executionEnvironment>> DockerContainer` is rendered floating as an autonomous top-level node without a parent `<<device>>` host node.
   - *Rule*: Software execution environments cannot exist without underlying computational hardware (physical server or virtual machine instance).
   - *Fix*: Nest `DockerContainer` within a parent `<<device>> AWS_EC2_Instance` or `<<node>> VirtualMachineHost`.

3. **Topology Impossibility (Direct Cable Across Hybrid Clouds)**:
   - *Defect*: Showing a direct physical cable between a public cloud Docker container and an on-premises private network database.
   - *Rule*: Communication across distinct physical domains must traverse an explicit gateway (e.g., `<<device>> VPN_Gateway` or `AWS DirectConnect Router`) via a secure tunneling protocol (`«IPsec VPN / BGP»`).

</details>

---

### Level 3: Production C++17 Distributed Component Assembly & Network Routing Engine

#### Challenge Description
Implement a production C++17 simulation engine that constructs a complete distributed topology graph. The engine must:
1. Model components with input and output ports.
2. Verify that interface method sets conform to structural subtyping contracts.
3. Compute the shortest communication path between any two components across a multi-hop deployment graph using Dijkstra's algorithm, calculating cumulative latency and identifying network bottlenecks.

<details>
<summary>Click to view production C++17 implementation</summary>

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <queue>
#include <limits>
#include <iomanip>

struct RouteHop {
    std::string targetNode;
    double latencyMs;
    std::string linkProtocol;
};

class DistributedNetworkRouter {
private:
    std::unordered_map<std::string, std::vector<RouteHop>> graph;
    std::unordered_map<std::string, std::string> componentPlacements; // Component -> Hosting Node

public:
    void placeComponent(const std::string& comp, const std::string& node) {
        componentPlacements[comp] = node;
    }

    void addBidirectionalLink(const std::string& nodeA, const std::string& nodeB, double latency, const std::string& protocol) {
        graph[nodeA].push_back({nodeB, latency, protocol});
        graph[nodeB].push_back({nodeA, latency, protocol});
    }

    struct PathResult {
        bool reachable;
        double totalLatency;
        std::vector<std::string> nodePath;
        std::vector<std::string> protocols;
    };

    PathResult routeBetweenComponents(const std::string& compSrc, const std::string& compDst) {
        std::string startNode = componentPlacements[compSrc];
        std::string goalNode = componentPlacements[compDst];

        if (startNode == goalNode) {
            return {true, 0.05, {startNode}, {"IPC Memory Bus"}};
        }

        // Dijkstra's Shortest Path Algorithm
        std::unordered_map<std::string, double> minLatency;
        std::unordered_map<std::string, std::pair<std::string, std::string>> prev; // Node -> {ParentNode, Protocol}

        for (const auto& [node, _] : graph) {
            minLatency[node] = std::numeric_limits<double>::infinity();
        }

        using QueueElement = std::pair<double, std::string>;
        std::priority_queue<QueueElement, std::vector<QueueElement>, std::greater<QueueElement>> pq;

        minLatency[startNode] = 0.0;
        pq.push({0.0, startNode});

        while (!pq.empty()) {
            auto [currLatency, u] = pq.top();
            pq.pop();

            if (currLatency > minLatency[u]) continue;
            if (u == goalNode) break;

            for (const auto& edge : graph[u]) {
                double newLatency = currLatency + edge.latencyMs;
                if (newLatency < minLatency[edge.targetNode]) {
                    minLatency[edge.targetNode] = newLatency;
                    prev[edge.targetNode] = {u, edge.linkProtocol};
                    pq.push({newLatency, edge.targetNode});
                }
            }
        }

        if (minLatency[goalNode] == std::numeric_limits<double>::infinity()) {
            return {false, 0.0, {}, {}};
        }

        // Reconstruct path
        std::vector<std::string> path;
        std::vector<std::string> protocols;
        std::string curr = goalNode;

        while (curr != startNode) {
            path.push_back(curr);
            auto [parent, proto] = prev[curr];
            protocols.push_back(proto);
            curr = parent;
        }
        path.push_back(startNode);
        std::reverse(path.begin(), path.end());
        std::reverse(protocols.begin(), protocols.end());

        return {true, minLatency[goalNode], path, protocols};
    }
};

int main() {
    DistributedNetworkRouter router;

    // Component Placements
    router.placeComponent("WebClient", "Edge_CDN_Node");
    router.placeComponent("AuthService", "East_Cluster_K8s");
    router.placeComponent("DatabaseShard", "Secure_Storage_Blade");

    // Network Topology
    router.addBidirectionalLink("Edge_CDN_Node", "Cloud_Edge_Router", 8.5, "TLS 1.3 / WAN");
    router.addBidirectionalLink("Cloud_Edge_Router", "East_Cluster_K8s", 2.1, "10GbE / VXLAN");
    router.addBidirectionalLink("East_Cluster_K8s", "Secure_Storage_Blade", 0.4, "NVMe-oF / RoCEv2");

    std::cout << ">>> Computing Routing from WebClient to DatabaseShard...\n";
    auto result = router.routeBetweenComponents("WebClient", "DatabaseShard");

    if (result.reachable) {
        std::cout << "Path found! Total Latency: " << result.totalLatency << " ms\n";
        std::cout << "Route Hop Progression:\n";
        for (size_t i = 0; i < result.nodePath.size(); ++i) {
            std::cout << "  [" << i << "] Node: " << result.nodePath[i];
            if (i < result.protocols.size()) {
                std::cout << " ---> via " << result.protocols[i] << " --->\n";
            } else {
                std::cout << " (Endpoint reached)\n";
            }
        }
    } else {
        std::cout << "Target component is unreachable in the physical topology.\n";
    }

    return 0;
}
```

</details>

---

## Pedagogical Review Questions & Examination Problems

1. **UML Metamodel Boundaries**: Contrast the operational purpose of a Port versus an internal Part within a Composite Component. Under what architectural condition does an architect use a Delegation Connector rather than an Assembly Connector?
2. **EEN Nesting Invariants**: Can an Execution Environment Node (`<<executionEnvironment>>`) directly host a physical device (`<<device>>`)? Explain why or why not based on the physical ontology of computing systems.
3. **Microservices Decomposition**: An organization migrates a monolithic system into 40 distinct microservice components. Explain how Component Diagrams with Provided/Required interface contracts prevent distributed dependency drift.
