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
```

## ⚙️ Installation & Build Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/jugal-ahir/DVRP.git
cd stochastic-routing-simulator
```

2. **Build LKH TSP Solver**

Navigate to the LKH directory and build the solver using mingw32-make (ensure you have MinGW installed):

```bash
cd thirdParty/lkh/LKH-3.0.7/src
mingw32-make
```

## 🚀 How to Run the Simulation

After building the LKH solver, navigate to the `scripts` directory to run the simulation:

```bash
cd ../../../..
cd scripts
python main.py --show-sim --max-tasks 1000 --policy lkh_batch_tsp --lambd 0.8 --service-tim 1 --generator uniform
```

## 🔄 Command Breakdown:

    --show-sim: Displays a live simulation plot.

    --max-tasks 1000: Simulates up to 1000 customer requests.

    --policy lkh_batch_tsp: Uses the LKH-based batch TSP solver.

    --lambd 0.8: Lambda value to control request intensity.

    --service-tim 1: Service time per task.

    --generator uniform: Task request generator type.

## 📝 License & Credits

This project is created as part of the *Fundamentals of Probability in Computing* course, focusing on the application of stochastic processes in urban logistics.

### 👩‍💻 Author:
- Jugal Vaghmashi, Archi Daga, Avadh Nandasana, Aneri Maniar 

### 📚 Guided By:
- Prof. Dhaval Patel and TA Kunj Kanzariya

### 📄 License:
This project is open-source and available under the [MIT License](LICENSE).

### 🤝 Acknowledgements:
- [Katta G Krishnamurthy's LKH TSP Solver](http://webhotel4.ruc.dk/~keld/research/LKH/)
- Visualization and simulation inspiration from similar research works on dynamic routing and stochastic modeling.

