#
#  NAME
#    problem_set1.py
#
#  DESCRIPTION
#    Open, view, and analyze raw extracellular data
#    In Problem Set 1, you will write create and test your own spike detector.
#

import numpy as np
import matplotlib.pylab as plt

def load_data(filename):
    """
    load_data takes the file name and reads in the data.  It returns two 
    arrays of data, the first containing the time stamps for when they data
    were recorded (in units of seconds), and the second containing the 
    corresponding voltages recorded (in units of microvolts - uV)
    """
    data = np.load(filename)[()];
    return np.array(data['time']), np.array(data['voltage'])
    
def bad_AP_finder(time,voltage):
    """
    This function takes the following input:
        time - vector where each element is a time in seconds
        voltage - vector where each element is a voltage at a different time
        
        We are assuming that the two vectors are in correspondance (meaning
        that at a given index, the time in one corresponds to the voltage in
        the other). The vectors must be the same size or the code
        won't run
    
    This function returns the following output:
        APTimes - all the times where a spike (action potential) was detected
         
    This function is bad at detecting spikes!!! 
        But it's formated to get you started!
    """
    
    #Let's make sure the input looks at least reasonable
    if (len(voltage) != len(time)):
        print "Can't run - the vectors aren't the same length!"
        APTimes = []
        return APTimes
    
    numAPs = np.random.randint(0,len(time))//10000 #and this is why it's bad!!
 
    # Now just pick 'numAPs' random indices between 0 and len(time)
    APindices = np.random.randint(0,len(time),numAPs)
    
    # By indexing the time array with these indices, we select those times
    APTimes = time[APindices]
    
    # Sort the times
    APTimes = np.sort(APTimes)
    
    return APTimes
    
def good_AP_finder(time,voltage):
    """
    This function takes the following input:
        time - vector where each element is a time in seconds
        voltage - vector where each element is a voltage at a different time
        
        We are assuming that the two vectors are in correspondance (meaning
        that at a given index, the time in one corresponds to the voltage in
        the other). The vectors must be the same size or the code
        won't run
    
    This function returns the following output:
        APTimes - all the times where a spike (action potential) was detected
    """
 
    APTimes = []
       
    #Let's make sure the input looks at least reasonable
    if (len(voltage) != len(time)):
        print "Can't run - the vectors aren't the same length!"
        return APTimes
    
    # We can detect a spike by some of it's properties 
    # 1. Going past 'point of no return' 
    # 2. Refractory period after a spike 
    # 3. Length of fluctation in voltage 
    #    (e.g. spikes should be about the same duration)
    # once we detect a spike, we can take the max from the range we 
    # think the spike is in, to give us the best chance of being inside 
    # the correct detection range 
    # we detect 35 times that a voltage is recorded above 450 (but really anything
    # above 200 is an AP) -- so we need to find the individual spikes within those
    # -- e.g. criteria 1 above should be enough to find the AP and then we just need
    # to filter the results. 
    
    # Whoa, so after looking at the hard data, there's no way I can use simple 
    # threshold detection to accurately pull out the action potentials.. 
    # One idea I had was the look for a sharp jump in voltage, and then find the 
    # local max, then not look for it again until voltage had dropped again 
    
    sampling_rate = time[1]-time[0]
    print 'Sampling rate: %fs' % sampling_rate
    
    # get the 'slope' of the voltage via diff and filter by steepness
    voltage_slope = plt.diff(voltage)

    # Group indexes into groups that are sequential (part of same waveform) 
    steep_values = plt.find(voltage_slope>43)    
    common_waveforms = []
    grouping_index = 0
    for i, value in enumerate(steep_values):
        if i == 0:
            # skip first iteration
            continue
        if (value - steep_values[i-1] == 1):
            # they are part of the same waveform            
            continue
        else: 
            # we found the end of a group
            common_waveforms.append(steep_values[grouping_index:i])
            grouping_index = i
    
    # For each group, find the local max
    for group in common_waveforms:
        APTimes.append(plt.find(voltage==max(voltage[group]))[0])
#    import pdb; pdb.set_trace()
    return time[APTimes]
    

def get_actual_times(dataset):
    """
    Load answers from dataset
    This function takes the following input:
        dataset - name of the dataset to get answers for

    This function returns the following output:
        APTimes - spike times
    """    
    return np.load(dataset)
    
def detector_tester(APTimes, actualTimes):
    """
    returns percentTrueSpikes (% correct detected) and falseSpikeRate
    (extra APs per second of data)
    compares actual spikes times with detected spike times
    This only works if we give you the answers!
    """
    
    JITTER = 0.025 #2 ms of jitter allowed
    
    #first match the two sets of spike times. Anything within JITTER_MS
    #is considered a match (but only one per time frame!)
    
    #order the lists
    detected = np.sort(APTimes)
    actual = np.sort(actualTimes)
    
    #remove spikes with the same times (these are false APs)
    temp = np.append(detected, -1)
    detected = detected[plt.find(plt.diff(temp) != 0)]
 
    #find matching action potentials and mark as matched (trueDetects)
    trueDetects = [];
    for sp in actual:
        z = plt.find((detected >= sp-JITTER) & (detected <= sp+JITTER))
        if len(z)>0:
            for i in z:
                zz = plt.find(trueDetects == detected[i])
                if len(zz) == 0:
                    trueDetects = np.append(trueDetects, detected[i])
                    break;
    percentTrueSpikes = 100.0*len(trueDetects)/len(actualTimes)
    
    #everything else is a false alarm
    totalTime = (actual[len(actual)-1]-actual[0])
    falseSpikeRate = (len(APTimes) - len(actualTimes))/totalTime
    
    # Added this for auto-evaluation based on criteria 
    pct_spike_eval = "PASS" if percentTrueSpikes > 90.0 else "FAIL"
    false_spike_eval = "PASS" if falseSpikeRate < 2.5 else "FAIL"
    overall_result = "FAIL" if pct_spike_eval == "FAIL" or false_spike_eval == "FAIL" else "PASS"    
    
    print 'Action Potential Detector Performance performance: '
    print '     Correct number of action potentials = %d' % len(actualTimes)
    print '     %s: Percent True Spikes = %f' % (pct_spike_eval, percentTrueSpikes)
    print '     %s: False Spike Rate = %f spikes/s' % (false_spike_eval, falseSpikeRate)
    print ''
    print 'Overall Evaluation: %s' % overall_result
    print ''
    return {'Percent True Spikes':percentTrueSpikes, 'False Spike Rate':falseSpikeRate}
    
    
def plot_spikes(time, voltage, APTimes, titlestr):
    """
    plot_spikes takes four arguments - the recording time array, the voltage
    array, the time of the detected action potentials, and the title of your
    plot.  The function creates a labeled plot showing the raw voltage signal
    and indicating the location of detected spikes with red tick marks (|)
    """
    plt.figure()
    
    # plot the raw data 
    plt.plot(time, voltage, 'b', hold=True)

    # mark the AP times 
    plt.plot(APTimes, [max(voltage)+50]*len(APTimes), 'r|', hold=True)

    # add labels 
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (uV)")
    plt.title(titlestr)    
    
    plt.show()
    
def plot_waveforms(time,voltage,APTimes,titlestr):
    """
    plot_waveforms takes four arguments - the recording time array, the voltage
    array, the time of the detected action potentials, and the title of your
    plot.  The function creates a labeled plot showing the waveforms for each
    detected action potential
    """

    plt.figure()
    # note the sampling rate: time[1] - time[0] = .000034375014s 
    # which can serve as our x-axis increments, so our x-axis is 
    # essentially an array from -.003 to .003, of len .006 / .000034375014
    xaxis = np.linspace(-.003, .003, num=(.006/.000034375014))
    xincrements = len(xaxis)
    
    for ap in APTimes:
        # yaxis is just the corresponding 6 ms from the voltage array (need to find the start and end index) 
        peak_index = plt.find(time == ap)[0]
        starting_index = peak_index - xincrements/2
        ending_index = peak_index + xincrements/2
        yaxis = voltage[starting_index:ending_index]
        plt.plot(xaxis, yaxis, 'b', hold=True)
        
    # add labels 
    plt.xlabel("Time (s)")
    plt.ylabel("Voltage (uV)")
    plt.title(titlestr)  

    plt.show()
    

        
##########################
#You can put the code that calls the above functions down here    
if __name__ == "__main__":
     t,v = load_data('spikes_example.npy')  
     actualTimes = get_actual_times('spikes_example_answers.npy')
#     t, v = load_data('spikes_easy_practice.npy')
#     actualTimes = get_actual_times('spikes_easy_practice_answers.npy')     
#     t, v = load_data('spikes_hard_practice.npy')
#     actualTimes = get_actual_times('spikes_hard_practice_answers.npy')     
     APTime = good_AP_finder(t,v)
     plot_spikes(t,v,APTime,'Action Potentials in Raw Signal')
     plot_waveforms(t,v,APTime,'Waveforms')
     detector_tester(APTime,actualTimes)


