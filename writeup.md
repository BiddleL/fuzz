How your fuzzer works

Mutation is handled by usage of generic and file specific mutators. In the generic mutator base the fuzzer does generic mutations that can be applied to all file types. So far this includes byte alteration, deletion and insertion.

The harness works by initialising the process. It then identifies the file type.  It then iterates through enumerated mutations with a new process each time
In the event of a crash the input, fault type and method of crash are recorded. If there is no crash the mutator is enumerated.

So far there are format specific mutations for CSV and JSON.
The CSV specific mutations include: inserting multiple rows in order to overflow, and replacing null bytes with non null bytes.
The JSON specifc mutations include: bit flips


What improvements can be made to your fuzzer?
Currently there is no degree of multithreading implemented in the harness. An implementation of this would allow faster execution of the fuzzer.
Implementation of formats other than CSV and JSON would make the fuzzer more well rounded.
Bit flipping could be a generic mutator
There is room to improve the descriptiveness of the crash logs.
The fuzzer stops once it has found a succesful payload. It could possibly be made to look for smaller or simpler payloads.
The fuzzer currently initialises an entire new process to test each mutation. Avoiding intialisation each time could reduce computational overhead.