# Introduction

- First few minutes spent with Introduction

# Project
- Are people real people?
- Is it a dog or a person?
- It's a lot about verification, how can we set-up a connection? 
- Example: policemen, should I trust him?
- Database should be created, to know with who they are dealing
- Different roles in the set-up
  - later

Based on open-source
- Hyperledger, ...
- Dashboard is there, very green software, it's running but is it robust?
- Onboarded new nodes, how to bring this to a stage where you can use it for production use cases
- More information about state
- Notepad with Notemonitor

- Hyperledger Indy is huge
- Lizzy is a handy wallet
- iDUnion is for everyone (companies, institutions, persons)

# Understand surrounding
- Hyperledger INDY
https://www.hyperledger.org/use/hyperledger-indy

- Have a note, put in information and get it out
- aries framework for clients (if you want to have a wallet)
  - handy wallet, cloud wallet, local wallet
- trustoverIP
- Holder has personal ID and wants to store that in the Data Wallet 
- baseID is germanID
- migrate as smartID in the phone
  - transaction will be written down
  - string on the ledger
  - ledger = base for all use cases
  - everyone is allowed to write but not everyone is allowed to read
  - ledger is on the right side: technology (all linked to certain governance)
- TrustOverIP should bring it all together
- Stewards run the nodes
- Read the docs on hyperledger indy, DID has a special role and is allowed to 
- Network

It's a lot about transaction, licenses, ID, credential for trainings etc., diploma
- Your country only cares about you if you have the proof that you're a citizen
- we all are driven by European regulations

consensus database = blockchain
- not changeable, just adding
- what happens if someone writes sth illegal in the blockchain
- siemens node on the dashboard
- node is a validator and writes it into the blockchain
- nodes do a consensus mechanism to be synced
  

query the files and display information
how is the node working?
steward wants to have information about specific nodes
uptime of every node: 98% => 10, 15, 25 nodes 
- decentralized
- that's major advantage
- benefit
  - governance point of view
  - not one rules them all
- request for information comes from external world
- you don't know what will be requested
- major advantage of this decentralized

requests are interesting, no credentials in the blockchain
- eID in our german ID
- Bundesdruckerei generated ID
  - credential of issueing
  - serial number, born at etc. 
- You don't know who requested it
  - smart eID will be checked e.g. from police, public key 

open bank account
- do you know digital bank?
- you never saw them before, here you have a direct connection

present ID
- annocratch
  
system that police has, has more information
- ledger only sees that Bundesdruckerei checked it
- between nodes always peertopeer
  - private IID fires
- different online shops, different names, they just need to check smartID - they don't need real birthdate 
- age is above eighteen
- does company use the data for sth else 


## Carbon footprint example
- no greenwashing possible anymore
- because product gets tracked
- you may not know who's the supplier
- a lot of calculation is going on in the background
- give me bill of material for specific product
  - switching cabinet with those products
  - calculated with greenhouse 

## BMW Fahrzeugzulassung
- already possible
- PersAuswG needs to be changed

## Is TÜV allowed to check car?
- BSI check

## Bavarian tax office
- Elster written by them
- partner project where they build together with Sparkasse a tool for small company where you have the tax report ready 
- based on tax report you will get a loan or not 

## Bundesanzeiger
- digital verifiable document (Handelsregisterauszug)
- issue credentials
- ID wallet Bundesdruckerei

## Company
- business through people
- issue credential => procura for employees
- MA Ausweis


We should know:
- What is in, what is not in? 
- Indy ReadtheDocs
https://hyperledger-indy.readthedocs.io/en/latest/
- Agent: Holds wallet
- My ledger is structured this way, we need this rule, you need to have this role to do transaction
- Which information do we have to know?

- spin off nodes VONnodes
- maybe build small version with nodes on PC (Genesis-file?)
- human devices working on rules

# Understand concrete task
- list - spreadsheet kind
- information out of the information we get 

- Defining and find out what can be done?
- Software infrastructure
- Node on operating system, node in container?
- Which information is factable?
  
## Personas
- Why should I care? 
- What does it offer for me?

- Stewards who run the node
- Governance Organizations

Most stewards are member of organizations

Who needs stewards? How can we look at the whole network? What could be interesting?

How can we present this? Visualization, Exploring

How can we get to this information? How can we have this up and running? 

Base is on Grafana

How to bring this to life, how to store it?

Internal, inner source sharing in Siemens

Are we able to set up? 

Some information on network architecture
- Hyperledger indy monitor

understand hyperledger, understand node-monitor
https://github.com/hyperledger/indy-node-monitor

All the visualization done in Grafana

Hold information of a digital twin
- different visualizations for different target groups
- options we than can discuss

We monitor the ledger !
- We want to see if everything is fine
- Then we want to dive deeper: Why is it yellow? Why is it red? 
- Unreachable node, push it to Slack Channels etc
- Do we have to care or not?

=> Deicsion support system

VON Network
