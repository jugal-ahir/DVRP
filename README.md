# 🚚 Stochastic Dynamic Vehicle Routing in Evolving Urban Logistics

This project simulates and optimizes vehicle routing in an urban logistics environment where task arrivals, traffic, and travel times are uncertain. We employ a **randomistic approach** using probability distributions and solve the route optimization via the **LKH-3.0.7** solver (Lin–Kernighan–Helsgaun).

## 🧠 Key Concepts

- **Stochastic Routing**: Task requests follow an exponential distribution, and travel times are modeled using a Gaussian distribution.
- **Dynamic Logistics**: The simulation adapts in real-time to randomly arriving delivery tasks.
- **Multivariate Gaussian Modeling**: Used to handle correlations between traffic, location, and service time.
- **LKH Solver Integration**: Uses the LKH-3.0.7 solver to find efficient solutions to the batch TSP (Traveling Salesman Problem).

## 📁 Project Structure

```bash
.
├── thirdParty/
│   └── lkh/
│       └── LKH-3.0.7/        # Contains the LKH TSP Solver
│           └── Makefile
├── scripts/                  # Contains the simulation script (main.py)
├── src/                      # Source files (if any custom modules are added)
├── results/                  # Folder to store simulation results and plots
└── README.md

## ⚙️ Installation & Build Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/your-username/stochastic-routing-simulator.git
cd stochastic-routing-simulator

2. **Build LKH TSP Solver**

Navigate to the LKH directory and build the solver using mingw32-make (ensure you have MinGW installed):

```bash
cd thirdParty/lkh/LKH-3.0.7
mingw32-make

