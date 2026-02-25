# PatchAgent

[![Build Status](https://github.com/cla7aye15I4nd/PatchAgent/actions/workflows/ci.yaml/badge.svg)](https://github.com/cla7aye15I4nd/PatchAgent/actions/workflows/ci.yaml)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)

> [!NOTE]  
> The original research repository is located at [osf.io/8k2ac](https://osf.io/8k2ac) and [PatchAgent-Artifact](https://github.com/cla7aye15I4nd/patchagent-artifact). 
> This repository is a production-focused fork dedicated to real-world bug fixing.

## 📣 News

- 🎉 [2025.11] PatchAgent win 🥈 Runner-up in Technical Impact Award of [CSAW Applied Research Competition (ARC) 2025](https://mlab.cyber.nyu.edu/csaw/finalists/#winners-2025)!
- 🎉 [2025.10] PatchAgent is accepted at [CSAW Applied Research Competition (ARC) 2025](https://mlab.cyber.nyu.edu/csaw/finalists/#finalists)!
- 🎉 [2025.08] PatchAgent is presented at [USENIX Security 2025](https://www.usenix.org/conference/usenixsecurity25/presentation/yu-zheng)!

## 📋 Overview

PatchAgent is an LLM-based program repair agent that mimics human expertise to automatically generate patches for real-world bugs. It integrates:

- **Language Server Protocol**: For accurate code navigation and analysis
- **Patch Verification**: For ensuring correct and safe fixes
- **Interaction Optimization**: To achieve human-like reasoning during vulnerability repair

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker (for OSS-Fuzz integration)
- Git

### Installation

```bash
# Pull the image
docker pull ghcr.io/cla7aye15i4nd/patchagent:latest

# Run the container
docker run -it --privileged ghcr.io/cla7aye15i4nd/patchagent:latest
```

### Environment Configuration

Create a `.env` file based on the template:

```bash
cp .env.template .env
# Edit .env with your API keys and configuration
```

## 💻 Usage Example

PatchAgent can be used to repair real-world bugs. Here's a simple example:

```python
from patchagent.agent.generator import agent_generator
from patchagent.builder import OSSFuzzBuilder, OSSFuzzPoC
from patchagent.parser.sanitizer import Sanitizer
from patchagent.task import PatchTask

# Initialize the repair task
patchtask = PatchTask(
    [OSSFuzzPoC("poc.bin", "libpng_read_fuzzer")],  # Proof of Concept file with target
    OSSFuzzBuilder(
        "libpng",                        # Project name
        "/path/to/libpng",               # Source code path
        "/path/to/oss-fuzz",             # OSS-Fuzz path
        [Sanitizer.AddressSanitizer],    # Sanitizer to use
    ),
)

# Initialize and run the repair process
patchtask.initialize()
patch = patchtask.repair(agent_generator())
print(f"Generated patch: {patch}")
```

## 🛠️ Development Setup

For development, we recommend using the VS Code devcontainer:

1. Install the [VS Code Remote Development Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)
2. Open the repository in VS Code
3. When prompted, click "Reopen in Container"

This will set up a fully configured development environment with all the necessary tools.

## 🔧 Supported Languages and Sanitizers

### Languages
- C/C++
- Java

### Sanitizers
- [AddressSanitizer (ASan)](https://github.com/google/sanitizers/wiki/AddressSanitizer)
- [MemorySanitizer (MSan)](https://github.com/google/sanitizers/wiki/MemorySanitizer)
- [UndefinedBehaviorSanitizer (UBSan)](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html)
- [ThreadSanitizer (TSan)](https://clang.llvm.org/docs/ThreadSanitizer.html)
- [Jazzer (Java fuzzing)](https://github.com/CodeIntelligenceTesting/jazzer)

## 🏆 Fixed Vulnerabilities

Below is a sample of the vulnerabilities fixed by PatchAgent. More will be disclosed as responsible disclosure periods end.

| Repository | Stars | Vulnerabilities |
| - | - | - |
| [assimp](https://github.com/assimp/assimp) | 11.4k | [#5763](https://github.com/assimp/assimp/pull/5763), [#5764](https://github.com/assimp/assimp/pull/5764), [#5765](https://github.com/assimp/assimp/pull/5765) |
| [libssh2](https://github.com/libssh2/libssh2) | 1.4k | [#1508](https://github.com/libssh2/libssh2/pull/1508) |
| [hdf5](https://github.com/HDFGroup/hdf5) | 0.6k | [#5201](https://github.com/HDFGroup/hdf5/pull/5201), [#5210](https://github.com/HDFGroup/hdf5/pull/5210) |
| [libredwg](https://github.com/LibreDWG/libredwg) | 1.0k | [#1061](https://github.com/LibreDWG/libredwg/pull/1061) |
| [Pcap++](https://github.com/seladb/PcapPlusPlus) | 2.8k | [#1678](https://github.com/seladb/PcapPlusPlus/pull/1678), [#1680](https://github.com/seladb/PcapPlusPlus/pull/1680), [#1699](https://github.com/seladb/PcapPlusPlus/pull/1699) |
| [yasm](https://github.com/yasm/yasm)| 1.4k | [#241](https://github.com/yasm/yasm/pull/241), [#242](https://github.com/yasm/yasm/pull/242), [#243](https://github.com/yasm/yasm/pull/243), [#244](https://github.com/yasm/yasm/pull/244), [#263](https://github.com/yasm/yasm/pull/263)| 
| [gtp5g](https://github.com/free5gc/gtp5g) | 76 | [#166](https://github.com/free5gc/gtp5g/pull/166) | 
| [Linux](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/log/?qt=grep&q=Ziyi+Guo) | oo | [cafc66](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=cafc6679824a026998d93e7435f6005f64e515d2  ), [856db3](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=856db37592021e9155384094e331e2d4589f28b1  ), [6d1dc8](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=6d1dc8014334c7fb25719999bca84d811e60a559), [9e7021](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9e7021d2aeae57c323a6f722ed7915686cdcc123), [026f65](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=026f6513c5880c2c89e38ad66bbec2868f978605), [47f79b](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=47f79b20e7fb885aa1623b759a68e8e27401ec4d), [29372f](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=29372f07f7969a2f0490793226ecf6c8c6bde0fa), [9f16d9](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=9f16d96e1222391a6b996a1b676bec14fb91e3b2), [84faa9](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=84faa91585fa22a161763f2fe8f84a602a196c87), [f51424](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=f514248727606b9087bc38a284ff686e0093abf1), [e1dccb](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e1dccb485c2876ac1318f36ccc0155416c633a48), [e55ac3](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e55ac348089e579fc224569c7bd90340bf2439f9), [820ba7](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=820ba7dd6859ef8b1eaf6014897e7aa4756fc65d), [e31fa6](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=e31fa691d0b1c07b6094a6cf0cce894192c462b3), [4dd1dd](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=4dd1dda65265ecbc9f43ffc08e333684cf715152), [0784c6](https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/commit/?id=0784c69c92858112d5ba326a6cf9254d84336d40) |
## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

For questions, bugs, or feature requests:
- Create [GitHub issues](https://github.com/cla7aye15I4nd/PatchAgent/issues)
- For direct communication related to PatchAgent, contact [Zheng Yu](https://www.dataisland.org)

## 📚 Citation

To cite PatchAgent in scientific publications, please use:

```bibtex
@inproceedings{PatchAgent,
  title     = {PatchAgent: A Practical Program Repair Agent Mimicking Human Expertise},
  author    = {Yu, Zheng and Guo, Ziyi and Wu, Yuhang and Yu, Jiahao and 
               Xu, Meng and Mu, Dongliang and Chen, Yan and Xing, Xinyu},
  booktitle = {34rd USENIX Security Symposium (USENIX Security 25)},
  year      = {2025}
}
```
