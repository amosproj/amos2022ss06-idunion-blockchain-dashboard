# IDunion blockchain dashboard (AMOS SS 2022)
## Project Summary
The goal of the project is to develop a metrics engine and a dashboard for the IDunion blockchain.
- The (UI-less) metrics engine
  - Collects data from the test instances of the blockchain and computes predefined metrics (a.k.a. KPIs, key performance indicators)
  - Allows for the registration of interest in these metrics and the provision of notifications if provided metric values match a defined (boolean) query
- The dashboard
  - Visualizes the metrics over time (using Grafana)
  - Can be configured by a user to meet their needs
  - Supports user accounts and role definitions where
  - Different roles get different default layouts
    - Can register interest in events where
  - Events correspond to metrics engine notifications 
    - Can display events

## Software Architecture
<img width="1313" alt="Bildschirmfoto 2022-05-10 um 18 08 56" src="https://user-images.githubusercontent.com/73983419/167785051-c35e75bd-4693-49d0-899a-8e77e9a5ce0e.png">
