# Security Policy & Architectural Symmetrical Boundaries

## 1. Definition of Architectural Vulnerabilities
Within the pTRC framework, security is defined as the maintenance of absolute integer bit-invariance. This system operates strictly within the boundaries of discrete arithmetic (\(\mathbb{Z}\)). 

The intentional or accidental introduction of continuous floating-point fields (\(\mathbb{R}\)), decimal variables (`floats`), or transcendental approximations (π, e) is classified as **Phase Dissipation and Analog Leakage**. 

Any modification or pull request that breaks the modulo-24/210 invariant lattice rules will be discarded immediately at the compiler pipeline layer.

## ⚖️ 2. Commercial Compliance & Warranty Void
While the open-source evaluation branch (GPLv3) allows academic modifications, notice is hereby given to all corporate entities:
*   Any introduction of floating-point arithmetic or continuous physics models into the core engine components instantly violates the structural integrity of the pTRC framework.
*   Modifications causing **Analog Leakage** will immediately void all commercial support agreements, architectural consulting certificates, and corporate licensing claims.

## 📧 3. Reporting Process
If you identify an calculation boundary bypass or a potential division-by-zero vulnerability that evades the rigid integer safety floors (such as the minimum 1-pixel constraint), do **NOT** open a public GitHub Issue.

Please report the mathematical anomaly privately to protect current commercial deployments:
📩 **g.wirminghaus@gmx.de**
