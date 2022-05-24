# IDunion blockchain dashboard (AMOS SS 2022)
**Table of Contents**
1. Project Summary
2. Software Architecture

## Project Summary

In the interest of our industry partner the mission is to identify data of possible interest and display it in a dashboard. 
By displaying the data in the dashboard it is easy and intuitive to get the impression of the network activity and ledger status. 
Based on the displayed information the industry partner can optimize it´s businesses.

The goal of the project is to develop a metrics engine and a dashboard for the IDunion blockchain.
1. The (UI-less) metrics engine
  1. Collects data from the test instances of the blockchain and computes predefined metrics (a.k.a. KPIs, key performance indicators)
  2. Allows for the registration of interest in these metrics and the provision of notifications if provided metric values match a defined (boolean) query
2. The dashboard
  1. Visualizes the metrics over time (using Grafana)
  2. Can be configured by a user to meet their needs
  3. Supports user accounts and role definitions where
  4. Different roles get different default layouts Can register interest in events where
  5. Events correspond to metrics engine notifications Can display events

## Software Architecture
![Software_Architecture_High_level](https://user-images.githubusercontent.com/73983419/167786311-3a55dbe2-7d1b-4db6-bf9c-58bed1cf2179.jpg)
