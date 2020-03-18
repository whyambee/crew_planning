#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 15 23:39:32 2020

@author: ymb
"""

import numpy as np
import matplotlib.pyplot as plt

# Upper bound on the incubation time; serves as code for healthy people
MaxIncubation=100000;


# Composition of the teams: 0 - at home, 1,2 etc - at various locations
#Teams=[20, 20]
#NumberTeams=len(Teams);
#Crew=sum(Teams);    #total number of workers

# Infection rates: at work and at home.
# to do: different infection rates for different teams
InfRateWork=.01;
InfRateHome=.001;

# setting up random schedule: Sch[m,t]=k if member k is on team 
# k during time slot t. Team 0 is staying at home

HperSlot=24;

def TwoTeamsPeriodic(team,period,periods):
    a=np.zeros([2*team,period*periods]);
    d1=team-.001;
    d2=period-.001;
    for i in range(2*team):
        for j in range(period*periods):
            a[i,j]=int(np.mod(np.floor(i/d1)+np.floor(j/d2),2))
    return(a.astype(int))

def TeamCountsInf(t,state,numberteams,assignment):
    count=np.zeros(numberteams);
    [crew,tslots]=np.shape(state)
    for i in range(crew):
        if (state[i,t-1]<MaxIncubation) and (0<state[i,t-1]):
            count[assignment[i,t]]+=1;
    return count;

def InfectWork(countinfected):
    infect=(1-InfRateWork/24*HperSlot)**countinfected<np.random.random()
    return infect

def InfectHome():
    infect=(1-InfRateHome*HperSlot/24)<np.random.random()
    return infect

def IncubationTime():
    return 24*np.random.lognormal(1.62,.418); # incubation period ~ lognormal: reference

def Run(assignment):
    # prepare state MaxIncubation if healthy, 0<T<MaxIncubation if latent
    # infected, 0 if symptomatic
    [Crew,Tslots]=np.shape(assignment);
    
    State=np.zeros([Crew,Tslots]);
    # Initialize:
    for i in range(Crew):
        State[i,0]=MaxIncubation; #all healthy

    # Actual run
    for i in range(Crew):        
        for t in range(1,Tslots):
            Count=TeamCountsInf(t-1,State,Crew,assignment);
            for i in range(Crew):
                if State[i,t-1]==MaxIncubation: # if healthy
                    if (assignment[i,t]==0 and InfectHome()) or (assignment[i,t]>0 and InfectWork(Count[assignment[i,t]])): #Infected
                        State[i,t]=IncubationTime();
                    else:
                        State[i,t]=MaxIncubation;
                elif State[i,t-1]>0:            # latent
                    State[i,t]=State[i,t-1]-HperSlot;
                elif State[i,t-1]<=0:
                    State[i,t]=0;
    return(State)

def Iterate(iterations, assignment):
    Infected=[];
    Working=[];
    for t in range(iterations):
        state=Run(assignment);
        Infected.append(sum(state[:,-1]<MaxIncubation));
        Working.append(sum(sum((state>0)*(assignment>0))));
    return [Infected,Working]

        
# run 
Assignment1=TwoTeamsPeriodic(15,2,30);

state=Run(Assignment1);
plt.plot(sum(state<MaxIncubation),'.',sum(state==0),'.')   
        