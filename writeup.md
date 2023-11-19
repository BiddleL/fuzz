# COMP6447 Major Project
## Group Members
- Daniel Blazevski
- Liam Biddle
- Ziqi Guo
- Shafi Rafiq (z5258434)

# How does the Fuzzer Work?
## Overview
As per the requirements of the project, our fuzzer is provided with a binary and a text file that contains a sample input. It then uses this to determine the file type, which is necessary in deciding the type of mutator that will be needed by the fuzzer to generate the inputs. Following this, the generated inputs are used by the fuzzer against the binary for a predetermined loop, which breaks upon discovering a crash. The input, fault type and method of crash are recorded by the harness, and outputted. A simple diagram is shown below to give a high level overview of this:
<pre>
<b>BINARY</b> |
       | ---------> <b>FILE TYPE CHEKCER</b>
<b>INPUT</b>  |                   |         
                   Determine File Type
                           |             
                           v                      
               <b>CALL FILE SPECIFIC MUTATOR</b> <------
                           |                      |
                     Generate Input               | No
                           |                      | Crash
                           v                      |
            <b>RUN MUTATED INPUTS AGAINST BINARY</b>  ---
                           |
                         Crash
                           |
                           v
                         <b>OUTPUT</b>     
</pre>

## Mutators
Our fuzzer uses several strategies when mutating the provided sample inputs in order to effectively crash the program (through segmentation faults, hanging the program, etc.). Using classes, we have created a set of common mutators in `/mutators/mutator_base.py` that can be used in the general case for all the file types being tested. The mutations present in this file mainly consists of:
- Randomly updating bytes (e.g. flipping random bits)
- Randomly adding new bytes
- Randomly deleting bytes

In addition to this, when our fuzzer determines the file type supplied, it will call the file format specific mutators found in the `/mutators` directory. These mutations focus on modifiying the sample inputs in specific ways to determine whether bugs exist in the file formats, such as adding to the input to cause an overflow, or adding specific characters to check for format string vulnerabilities, etc. A summary of the mutations being made are shown below:

| File Type | Mutations |
| ---------- | ---------- |
| CSV | Mutate bytes in random cells<br/>Replace bytes in random cells<br/>Delete bytes in random cells<br/>Add new rows with random bytes to invoke an overflow<br/>Convert null bytes to random values|
| JSON | Add random amounts of (key: str, value: int) JSON objects to the input<br/>Add random amounts of (key: str, value: str) JSON objects to the input<br/>Mutate random bits in the provided input|
| Plain text/ELF | Mutating input to be of large lengths to cause overflows<br/>The above inputs consist of chars, nulls, newlines, etc.<br/>Adding large positive and negative numbers to cause int overflow/underflow<br/>Format specifiers added to generated input |
| XML | Mutating the XML tag value<br/>Mutating attributes of XML elements<br/>Adding excessive ammounts of tags to invoke an overflow |
| JPEG |  Adding a new quantization table with random bytes</br>hanging a random quantization table with random bytes</br>Changing a huffman table with random bytes</br>Changing the frame's height and weight to random bytes</br>Flipping the body of the image</br>|
| PDF | [Mutations here] |

## Harness
The harness begins by initialising the process. Following this, it receives the binary and sample input file and determines the file type using a combination of the header, file content and structures. With the knowledge of the file type, it calls the specific file type mutator to generate inputs to begin the process of fuzzing the binary.

Once it finds an input that causes the binary to crash (segmentation fault, hanging, etc.), it logs the index of the input and the exit code received. It also logs the method used to obtain the input, as well as the input length. This information is then written to a text file. 

# What kinds of bugs the fuzzer can find?

The fuzzer we created is able to determine crashes a binary may have in relation to its memory, caused by errors such as segmentation faults and timeouts/hanging. Upon discovery of such errors it will record and output the circumstances involved with the bug, which, as aforementioned, includes the input used, the length of the input, the method used to generate the input, etc. In addition to this, the fuzzer also has the ability to discover whether the binary is exploitable using overflow/underflows (e.g. buffer/int overflow) and/or format strings using mutations that target these vulnerabilities (mentioned under file specific mutations section).

# Possible Improvements

There are various ways to enhance the current capabilities of the fuzzer, the most significant method being the use of a smarter, self-learning manner in which the inputs are generated. In other words, the mutations generated have an element of calculated randomness in that they follow certain rules to create inputs that allow for a more accurate result. A very simple example of such an implementation could be that, upon discovery of a buffer overflow due to a segmentation fault, inputs of increasing/decreasing sizes are generated to narrow down the length until the exact point at which the overflow occurs is determined. This could be further enhanced by implementing methods that take into account code coverage.

Along with this, another possible improvement could be the manner in which the results are outputted. While the input that caused the crash is indeed currently outputted to a file, a CLI could be implemented that provides the user with an interactive report to view/analyse the findings more thoroughly and conveniently.
