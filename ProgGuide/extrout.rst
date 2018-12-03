
.. index::
   Integrating External Routines

==================================
11. Integrating External Routines
==================================

.. contents::
   :depth: 5

----------------------
Introduction
----------------------

Application code written in M can call application code written in C (or which uses a C compatible call) and vice versa.

.. note::
   This C code shares the process address space with the YottaDB run-time library and M application code. Bugs in C code may result in difficult to diagnose failures to occur in places not obviously related to the cause of the failure.

------------------------
Access to non-M Routines
------------------------

In YottaDB, calls to C language routines may be made with the following syntax:

.. parsed-literal::
   DO &[packagename.]name[^name][parameter-list]

or as an expression element,

.. parsed-literal::
   $&[packagename.]name[^name][parameter-list]

Where packagename, like the name elements, is a valid M name. Because of the parsing conventions of M, the identifier between the ampersand (&) and the optional parameter-list has precisely constrained punctuation - a later section describes how to transform this into a more richly punctuated name, should that be appropriate for the called function. While the intent of the syntax is to permit the name^name to match an M labelref, there is no semantic implication to any use of the up-arrow (^). For more information on M names, labelrefs and parameter-lists, refer to `Chapter 5: “General Language Features of M” <https://docs.yottadb.com/ProgrammersGuide/langfeat.html>`_.

Example:

.. parsed-literal::
   ;Call external routine rtn1
   DO &rtn1
   ;Call int^exp in package "mathpak" with one parameter: the expression val/2
   DO &mathpak.int^exp(val/2)
   ;Call the routine sqrt with the value "2"
   WRITE $&sqrt(2)
   ;Call the routine get parms, with the parameter "INPUT" and the variable "inval", passed by reference.
   DO &getparms("INPUT",.inval)
   ;Call program increment in package "mathpak" without specifying a value for the first argument and the variable "outval" passed by reference as the second argument. All arguments which do not specify a value translate to default values in the increment program.  
   Do &mathpak.increment(,.outval) 

The called routines follow the C calling conventions. They must be compiled as position independent code and linked as a shareable library.

----------------------------------
Creating a Shareable Library
----------------------------------

The method of creating a shareable library varies by the operating system. The following examples illustrate the commands on an IBM pSeries (formerly RS/6000) AIX system.

Example:

.. parsed-literal::
   $ cat increment.c
   int increment(int count, float \*invar, float \*outvar)
   {
       \*outvar=*invar+1.0;
        return 0;
   }
   $ cat decrement.c
   int decrement(int count, float \*invar, float \*outvar)
   {
    \*outvar=\*invar-1.0;
     return 0;
    }        


On IBM pSeries AIX:

Example:

.. parsed-literal::
   $ cc -c -I$ydb_dist increment.c decrement.c
   $ ld -o libcrement.so increment.o decrement.o -G -bexpall -bnoentry -bh:4 -lc

.. note::
   Refer to the AIX V4.2 documentation of the ld(1) AIX command for information on shareable libraries under AIX V4.2. 

On Linux x86:

Example:

.. parsed-literal::
   % gcc -c -fPIC -I$ydb_dist increment.c decrement.c
   % gcc -o libcrement.so -shared increment.o decrement.o

--------------------------
Using External Calls
--------------------------

The functions in programs increment and decrement are now available to YottaDB through the shareable library libcrement.sl or libcrement.so, or though the DLL as libcrement.dll, depending on the specific platform. The suffix .sl is used throughout the following examples to represent .sl, .so, or .dll. Be sure to use the appropriate suffix for your platform.

YottaDB uses an "external call table" to map the typeless data of M into the typed data of C, and vice versa. The external call table has a first line containing the pathname of the shareable library file followed by one or more specification lines in the following format:

.. parsed-literal::
   entryref: return-value routine-name (parameter, parameter, ... )        

where entryref is an M entryref, return-value is ydb_long_t, ydb_status_t, or void, and parameters are in the format: 

.. parsed-literal::
   direction:type [num]

where [num] indicates a pre-allocation value explained later in this chapter.

Legal directions are I, O, or IO for input, output, or input/output, respectively.

The following table describes the legal types defined in the C header file $ydb_dist/libyottadb.h:

**Type: Usage**

Void: Specifies that the function does not return a value.

ydb_status_t : Type int. If the function returns zero (0), then the call was successful. If it returns a non-zero value, YottaDB will signal an error upon returning to M.

ydb_long_t : 32-bit signed integer on 32-bit platforms and 64-bit signed integer on 64-bit platforms.

ydb_ulong_t : 32-bit unsigned integer on 32-bit platforms and 64-bit signed integer on 64-bit platforms.

ydb_long_t* : For passing a pointer to long [integers].

ydb_float_t* : For passing a pointer to floating point numbers.

ydb_double_t* : Same as above, but double precision.

ydb_char_t*: For passing a "C" style string - null terminated.

ydb_char_t** : For passing a pointer to a "C" style string.

ydb_string_t* : For passing a structure in the form {int length;char \*address}. Useful for moving blocks of memory to or from YottaDB.

ydb_pointertofunc_t : For passing callback function pointers. For details see `“Callback Mechanism” <https://docs.yottadb.com/ProgrammersGuide/extrout.html#callback-mechanism>`_.

**Note:**

If an external call's function argument is defined in the external call table, YottaDB allows invoking that function without specifying a value of the argument. All non-trailing and output-only arguments which do not specify a value translate to the following default values in C: 

* All numeric types: 0 
* ydb_char_t * and ydb_char_t \*\*: Empty string 
* ydb_string_t \*: A structure with 'length' field matching the preallocation size and 'address' field being a NULL pointer. 

In the mathpak package example, the following invocation translate inval to the default value, that is, 0.

.. parsed-literal::
   YDB>do &mathpak.increment(,.outval)

If an external call's function argument is defined in the external call table and that function is invoked without specifying the argument, ensure that the external call function appropriately handles the missing argument. As a good programming practice, always ensure that count of arguments defined in the external call table matches the function invocation. 

libyottadb.h also includes definitions for the following entry points exported from libgtmshr: 

.. parsed-literal::
   void ydb_hiber_start(ydb_uint_t mssleep);
   void ydb_hiber_start_wait_any(ydb_uint_t mssleep)
   void ydb_start_timer(ydb_tid_t tid, ydb_int_t time_to_expir, void (\*handler)(), ydb_int_t hdata_len, void \\\*hdata);
   void ydb_cancel_timer(ydb_tid_t tid);

where:

* mssleep - milliseconds to sleep
* tid - unique timer id value
* time_to_expir - milliseconds until timer drives given handler
* handler - function pointer to handler to be driven
* hdata_len - 0 or length of data to pass to handler as a parameter
* hdata - NULL or address of data to pass to handler as a parameter

ydb_hiber_start() always sleeps until the time expires; ydb_hiber_start_wait_any() sleeps until the time expires or an interrupt by any signal (including another timer). ydb_start_timer() starts a timer but returns immediately (no sleeping) and drives the given handler when time expires unless the timer is canceled.

.. note::
   YottaDB continues to support xc_* equivalent types of ydb_* for upward compatibility. gtmxc_types.h explicitly marks the xc_* equivalent types as deprecated.

* Parameter-types that interface YottaDB with non-M code using C calling conventions must match the data-types on their target platforms. Note that most addresses on 64-bit platforms are 8 bytes long and require 8 byte alignment in structures whereas all addresses on 32-bit platforms are 4 bytes long and require 4-byte alignment in structures.
* Though strings with embedded zeroes are sent as input to external routines, embedded zeroes in output (or return value) strings of type ydb_char_t may cause string truncation because they are treated as terminators.
* If your interface uses ydb_long_t or ydb_ulong_t types but your interface code uses int or signed int types, failure to revise the types so they match on a 64-bit platform will cause the code to fail in unpleasant, potentially dangerous and hard to diagnose ways.

The first parameter of each called routine is an int (for example, int argc in decrement.c and increment.c) that specifies the number of parameters passed. This parameter is implicit and only appears in the called routine. It does not appear in the call table specification, or in the M invocation. If there are no explicit parameters, the call table specification will have a zero (0) value because this value does not include itself in the count. If there are fewer actual parameters than formal parameters, the call is determined from the parameters specified by the values supplied by the M program. The remaining parameters are undefined. If there are more actual parameters than formal parameters, YottaDB reports an error.

There may be only a single occurrence of the type ydb_status_t for each entryref.

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Database Encryption Extensions to the YottaDB External Interface
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

To support Database Encryption, YottaDB provides a reference implementation which resides in $ydb_dist/plugin/gtmcrypt.

The reference implementation includes:

* A $ydb_dist/plugin/gtmcrypt sub-directory with all source files and scripts. The scripts include those needed to build/install libgtmcrypt.so and "helper" scripts, for example, add_db_key.sh (see below).
* The plugin interface that YottaDB expects is defined in gtmcrypt_interface.h. Never modify this file - it defines the interface that the plugin must provide.
* $ydb_dist/plugin/libgtmcrypt.so is the shared library containing the executables which is dynamically linked by YottaDB and which in turn calls the encryption packages. If the $ydb_dist/utf8 directory exists, then it should contain a symbolic link to ../plugin.
* Source code is provided in the file $ydb_dist/plugin/gtmcrypt/source.tar which includes build.sh and install.sh scripts to respectively compile and install libgtmcrypt.so from the source code.

To support the implementation of a reference implementation, YottaDB provides additional C structure types (in the libyottadb.h file):

* gtmcrypt_key_t - a datatype that is a handle to a key. The YottaDB database engine itself does not manipulate keys. The plug-in keeps the keys, and provides handles to keys that the YottaDB database engine uses to refer to keys.
* xc_fileid_ptr_t - a pointer to a structure maintained by YottaDB to uniquely identify a file. Note that a file may have multiple names - not only as a consequence of absolute and relative path names, but also because of symbolic links and also because a file system can be mounted at more than one place in the file name hierarchy. YottaDB needs to be able to uniquely identify files.

Although not required to be used by a customized plugin implementation, YottaDB provides (and the reference implementation uses) the following functions for uniquely identifying files:

* xc_status_t ydb_filename_to_id(xc_string_t \*filename, xc_fileid_ptr_t \*fileid) - function that takes a file name and provides the file id structure for that file.
* xc_status_t ydb_is_file_identical(xc_fileid_ptr_t fileid1, xc_fileid_ptr_t fileid2) - function that determines whether two file ids map to the same file.
* ydb_xcfileid_free(xc_fileid_ptr_t fileid) - function to release a file id structure.

Mumps, MUPIP and DSE processes dynamically link to the plugin interface functions that reside in the shared library. The functions serve as software "shims" to interface with an encryption library such as libmcrypt or libgpgme/libgcrypt.

The plugin interface functions are:

* gtmcrypt_init()
* gtmcrypt_getkey_by_name()
* gtmcrypt_getkey_by_hash()
* gtmcrypt_hash_gen()
* gtmcrypt_encode()
* gtmcrypt_decode()
* gtmcrypt_close()
* and gtmcrypt_strerror()

A YottaDB database consists of multiple database files, each of which has its own encryption key, although you can use the same key for multiple files. Thus, the gtmcrypt* functions are capable of managing multiple keys for multiple database files. Prototypes for these functions are in gtmcrypt_interface.h.

The core plugin interface functions, all of which return a value of type ydb_status_t are:

* gtmcrypt_init() performs initialization. If the environment variable $ydb_passwd exists and has an empty string value, YottaDB calls gtmcrypt_init() before the first M program is loaded; otherwise it calls gtmcrypt_init() when it attempts the first operation on an encrypted database file.
* Generally, gtmcrypt_getkey_by_hash or, for MUPIP CREATE, gtmcrypt_getkey_by_name perform key acquisition, and place the keys where gtmcrypt_decode() and gtmcrypt_encode() can find them when they are called.
* Whenever YottaDB needs to decode a block of bytes, it calls gtmcrypt_decode() to decode the encrypted data. At the level at which YottaDB database encryption operates, it does not matter what the data is - numeric data, string data whether in M or UTF-8 mode and whether or not modified by a collation algorithm. Encryption and decryption simply operate on a series of bytes.
* Whenever YottaDB needs to encode a block of bytes, it calls gtmcrypt_encode() to encode the data.
* If encryption has been used (if gtmcrypt_init() was previously called and returned success), YottaDB calls gtmcrypt_close() at process exit and before generating a core file. gtmcrypt_close() must erase keys in memory to ensure that no cleartext keys are visible in the core file.

More detailed descriptions follow.

* gtmcrypt_key_t \*gtmcrypt_getkey_by_name(ydb_string_t \*filename) - MUPIP CREATE uses this function to get the key for a database file. This function searches for the given filename in the memory key ring and returns a handle to its symmetric cipher key. If there is more than one entry for the given filename , the reference implementation returns the entry matching the last occurrence of that filename in the master key file.
* ydb_status_t gtmcrypt_hash_gen(gtmcrypt_key_t \*key, ydb_string_t \*hash) - MUPIP CREATE uses this function to generate a hash from the key then copies that hash into the database file header. The first parameter is a handle to the key and the second parameter points to 256 byte buffer. In the event the hash algorithm used provides hashes smaller than 256 bytes, gtmcrypt_hash_gen() must fill any unused space in the 256 byte buffer with zeros.
* gtmcrypt_key_t \*gtmcrypt_getkey_by_hash(ydb_string_t \*hash) - YottaDB uses this function at database file open time to obtain the correct key using its hash from the database file header. This function searches for the given hash in the memory key ring and returns a handle to the matching symmetric cipher key. MUPIP LOAD, MUPIP RESTORE, MUPIP EXTRACT, MUPIP JOURNAL and MUPIP BACKUP -BYTESTREAM all use this to find keys corresponding to the current or prior databases from which the files they use for input were derived.
* ydb_status_t gtmcrypt_encode(gtmcrypt_key_t \*key, ydb_string_t \*inbuf, ydb_string_t \*outbuf) and ydb_status_t gtmcrypt_decode(gtmcrypt_key_t \*key, ydb_string_t \*inbuf, ydb_string_t \*outbuf)- YottaDB uses these functions to encode and decode data. The first parameter is a handle to the symmetric cipher key, the second is a pointer to the block of data to encode or decode, and the third is a pointer to the resulting block of encoded or decoded data. Using the appropriate key (same key for a symmetric cipher), gtmcrypt_decode() must be able to decode any data buffer encoded by gtmcrypt_encode(), otherwise the encrypted data is rendered unrecoverable. As discussed earlier, YottaDB requires the encrypted and cleartext versions of a string to have the same length.
* char \*gtmcrypt_strerror() - YottaDB uses this function to retrieve addtional error context from the plug-in after the plug-in returns an error status. This function returns a pointer to additional text related to the last error that occurred. YottaDB displays this text as part of an error report. In a case where an error has no additional context or description, this function returns a null string.

The complete source code for reference implementations of these functions is provided, licensed under the same terms as YottaDB. You are at liberty to modify them to suit your specific YottaDB database encryption needs. 

For more information and examples, refer to `Database Encryption <https://docs.yottadb.com/AdminOpsGuide/encryption.html>`_ in the Administration and Operations Guide.

++++++++++++++++++++++++++++++++++++
Pre-allocation of Output Parameters
++++++++++++++++++++++++++++++++++++

The definition of parameters passed by reference with direction output can include specification of a pre-allocation value. This is the number of units of memory that the user wants YottaDB to allocate before passing the parameter to the external routine. For example, in the case of type ydb_char_t \*, the pre-allocation value would be the number of bytes to be allocated before the call to the external routine.

Specification of a pre-allocation value should follow these rules:

* Pre-allocation is an unsigned integer value specifying the number of bytes to be allocated on the system heap with a pointer passed into the external call.
* Pre-allocating on a type with a direction of input or input/output results in a YottaDB error.
* Pre-allocation is meaningful only on types ydb_char_t * and ydb_string_t \*. On all other types the pre-allocation value specified will be ignored and the parameter will be allocated a default value for that type. With ydb_string_t * arguments make sure to set the 'length' field appropriately before returning control to YottaDB. On return from the external call, YottaDB uses the value in the length field as the length of the returned value, in bytes.
* If the user does not specify any value, then the default pre-allocation value would be assigned to the parameter.
* Specification of pre-allocation for "scalar" types (parameters which are passed by value) is an error.

.. note::
   Pre-allocation is optional for all output-only parameters except ydb_string_t * and ydb_char_t \*. Pre-allocation yields better management of memory for the external call. 

+++++++++++++++++++++++++++++
Callback Mechanism
+++++++++++++++++++++++++++++

YottaDB exposes certain functions that are internal to the YottaDB runtime library for the external calls via a callback mechanism. While making an external call, YottaDB populates and exposes a table of function pointers containing addresses to call-back functions.

+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
| Index    | Function            | Argument           | Type               | Description                                                                                                                |
+==========+=====================+====================+====================+============================================================================================================================+
| 0        | hiber_start         |                    |                    | sleep for a specified time                                                                                                 |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | slp_time           | integer            | milliseconds to sleep                                                                                                      |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
| 1        | hiber_start_wait_any|                    |                    | sleep for a specified time or until any interrupt, whichever comes first                                                   |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | slp_time           | integer            | milliseconds to sleep                                                                                                      |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
| 2        | start_timer         |                    |                    | start a timer and invoke a handler function when the timer expires                                                         |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | tid                | integer            | unique user specified identifier for this timer                                                                            |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | time_to_expire     | integer            | milliseconds before handler is invoked                                                                                     |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | handler            | pointer to function| specifies the entry of the handler function to invoke                                                                      |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | hlen               | integer            | length of data to be passed via the hdata argument                                                                         |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | hdata              | pointer to char    | data (if any) to pass to the handler function                                                                              |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
| 3        | cancel_timer        |                    |                    | stop a timer previously started with start_timer(), if it has not yet expired                                              |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | tid                | integer            | unique user specified identifier of the timer to cancel                                                                    |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
| 4        | ydb_malloc          |                    |                    | allocates process memory from the heap                                                                                     |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | <return-value>     | pointer to void    | address of the allocated space                                                                                             |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | space needed       | 32-bit platforms:  | bytes of space to allocate. This has the same signature as the system malloc() call.                                       |
|          |                     |                    | 32-bit unsigned    |                                                                                                                            |
|          |                     |                    | integer            |                                                                                                                            |
|          |                     |                    |                    |                                                                                                                            |
|          |                     |                    | 64-bit platforms:  |                                                                                                                            |
|          |                     |                    | 64-bit unsigned    |                                                                                                                            |
|          |                     |                    | integer            |                                                                                                                            |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
| 5        | ydb_free            |                    |                    | return memory previously allocated with ydb_malloc()                                                                       |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+
|          |                     | free_address       | pointer to void    | address of the previously allocated space                                                                                  |
+----------+---------------------+--------------------+--------------------+----------------------------------------------------------------------------------------------------------------------------+

The external routine can access and invoke a call-back function in any of the following mechanisms: 

* While making an external call, YottaDB sets the environment variable GTM_CALLIN_START to point to a string containing the start address (decimal integer value) of the table described above. The external routine needs to read this environment variable, convert the string into an integer value and should index into the appropriate entry to call the appropriate YottaDB function.
* YottaDB also provides an input-only parameter type ydb_pointertofunc_t that can be used to obtain call-back function pointers via parameters in the external routine. If a parameter is specified as I:ydb_pointertofunc_t and if a numeric value (between 0-5) is passed for this parameter in M, YottaDB interprets this value as the index into the callback table and passes the appropriate callback function pointer to the external routine.

.. note::
   YottaDB strongly discourages the use of signals, especially SIGALARM, in user written C functions. YottaDB assumes that it has complete control over any signals that occur and depends on that behavior for recovery if anything should go wrong. The use of exposed timer APIs should be considered for timer needs.

++++++++++++++++++++++++++++++++++++
Limitations on the External Program
++++++++++++++++++++++++++++++++++++

Since both YottaDB runtime environment and the external C functions execute in the same process space, the following restrictions apply to the external functions:

* YottaDB is designed to use signals and has signal handlers that must function for YottaDB to operate properly. The timer related call-backs should be used in place of any library or system call which uses SIGALRM such as sleep(). Use of signals by external call code may cause YottaDB to fail.
* Use of the YottaDB provided malloc and free, creates an integrated heap management system, which has a number of debugging tools. YottaDB recommends the usage of ydb_malloc/ydb_free in the external functions that provides better debugging capability in case memory management problems occur with external calls.
* Use of exit system call in external functions is strongly discouraged. Since YottaDB uses exit handlers to properly shutdown runtime environment and any active resources, the system call _exit should never be used in external functions.
* YottaDB uses timer signals so often that the likelihood of a system call being interrupted is high. So, all system calls in the external program can return EINTR if interrupted by a signal.
* Handler functions invoked with start_timer must not invoke services that are identified by the Operating System documentation as unsafe for signal handlers (or not identified as safe) - consult the system documentation or man pages for this information. Such services cause non-deterministic failures when they are interrupted by a function that then attempts to call them, wrongly assuming they are re-entrant.

The ydb_stdout_stderr_adjust() function checks whether stdout (file descriptor 1) and stderr (file descriptor 2) are the same file. If they are the same file, the function routes writes to stdout instead of stderr. This ensures that output appears in the order in which it was written. Otherwise, owing to IO buffering, output can appear in an order different from that in which it was written. Application code that mixes C and M code, and explicitly redirects stdout or stderr should call this function as soon as possible after the redirection. Refer to the function definition in the `Multi-Language Programmer's Guide <https://docs.yottadb.com/MultiLangProgGuide/MultiLangProgGuide.html#ydb-stdout-stderr-adjust>`_.

++++++++++++++++++++++++++++++++++++++++
Examples of Using External Calls
++++++++++++++++++++++++++++++++++++++++

.. parsed-literal::
   foo: void bar (I:ydb_float_t*, O:ydb_float_t*)

There is one external call table for each package. The environment variable "ydb_xc" must name the external call table file for the default package. External call table files for packages other than the default must be identified by environment variables of the form "ydb_xc_name".

The first of the external call tables is the location of the shareable library. The location can include environment variable names.

Example: 

.. parsed-literal::
   % echo $ydb_xc_mathpak
   /user/joe/mathpak.xc
   % echo lib /usr/
   % cat mathpak.xc
   $lib/mathpak.sl
   exp: ydb_status_t xexp(I:ydb_float_t*, O:ydb_float_t*)
   % cat exp.c
   ...
   int xexp(count, invar, outvar)
   int count;
   float \*invar;
   float \*outvar;
   {
    ...
   }
   % ydb
   ... 
   YDB>d &mathpak.exp(inval,.outval)
   YDB>

Example : For preallocation: 

.. parsed-literal::
   % echo $ydb_xc_extcall
   /usr/joe/extcall.xc
   % cat extcall.xc
   /usr/lib/extcall.sl
   prealloc: void ydb_pre_alloc_a(O:ydb_char_t \*[12])
   % cat extcall.c
   #include <stdio.h>
   #include <string.h>
   #include "libyottadb.h"
   void ydb_pre_alloc_a (int count, char \*arg_prealloca)
   {
    strcpy(arg_prealloca, "New Message");
    return;
   }

Example : for call-back mechanism

.. parsed-literal::
   % echo $ydb_xc 
   /usr/joe/callback.xc 
   % cat /usr/joe/callback.xc 
   $MYLIB/callback.sl 
   init:     void   init_callbacks() 
   tstslp:  void   tst_sleep(I:ydb_long_t) 
   strtmr: void   start_timer(I:ydb_long_t, I:ydb_long_t) 
   % cat /usr/joe/callback.c 
   #include <stdio.h> 
   #include <stdlib.h> 
    
   #include "libyottadb.h" 
 
   void \*\*functable; 
   void (\*setup_timer)(int , int , void (*)() , int , char \*); 
   void (\*cancel_timer)(int ); 
   void (\*sleep_interrupted)(int ); 
   void (\*sleep_uninterrupted)(int ); 
   void* (\*malloc_fn)(int); 
   void (\*free_fn)(void*); 
 
   void  init_callbacks (int count) 
   { 
      char \*start_address; 
    
      start_address = (char \*)getenv("GTM_CALLIN_START"); 
       
      if (start_address == (char \*)0) 
       { 
        fprintf(stderr,"GTM_CALLIN_START is not set\n"); 
        return; 
       } 
      functable = (void \*\*)atoi(start_address); 
      if (functable == (void \*\*)0) 
      { 
       perror("atoi : "); 
       fprintf(stderr,"addresses defined by GTM_CALLIN_START not a number\n"); 
       return; 
      } 
      sleep_uninterrupted = (void (*)(int )) functable[0]; 
      sleep_interrupted = (void (*)(int )) functable[1]; 
      setup_timer = (void (*)(int , int, void (*)(), int, char \*)) functable[2]; 
      cancel_timer = (void (*)(int )) functable[3]; 
                                                                      
      malloc_fn = (void* (*)(int)) functable[4]; 
      free_fn = (void (*)(void*)) functable[5]; 
                                                                              
      return; 
   } 
                                                                     
   void  sleep (int count, int time) 
   { 
      (\*sleep_uninterrupted)(time); 
   } 
                                                                                    
   void timer_handler () 
   { 
      fprintf(stderr,"Timer Handler called\n"); 
      /* Do something \*/ 
   } 
                                                                                          
   void  start_timer (int count, int time_to_int, int time_to_sleep) 
   { 
      (\*setup_timer)((int )start_timer, time_to_int, timer_handler, 0, 0); 
      return; 
   } 
   void* xmalloc (int count) 
   {   
     return (\*malloc_fn)(count); 
   } 
                                                                                                
   void  xfree(void* ptr) 
   { 
     (\*free_fn)(ptr); 
   }

Example:ydb_malloc/ydb_free callbacks using ydb_pointertofunc_t

.. parsed-literal::
   % echo $ydb_xc
   /usr/joe/callback.xc
   % cat /usr/joe/callback.xc
   /usr/lib/callback.sl
   init: void init_callbacks(I:ydb_pointertofunc_t, I:ydb_pointertofunc_t)
   % ydb
   YDB> do &.init(4,5)
   YDB>
   % cat /usr/joe/callback.c
   #include <stdio.h>
   #include <stdlib.h>
   #include "libyottadb.h"
   void* (\*malloc_fn)(int);
   void (\*free_fn)(void*);
   void init_callbacks(int count, void* (\*m)(int), void (\*f)(void*))
   {
       malloc_fn = m;
       free_fn = f;
   }

-----------------------------------------
Calls from External Routines: Call-Ins
-----------------------------------------

Call-In is a framework supported by YottaDB that allows a C/C++ program to invoke an M routine within the same process context. YottaDB provides a well-defined Call-In interface packaged as a run-time shared library that can be linked into an external C/C++ program.

+++++++++++++++++++++++++++
Relevant Files for Call-Ins
+++++++++++++++++++++++++++

To facilitate Call-Ins to M routines, the YottaDB distribution directory ($ydb_dist) contains the following files:

* libgtmshr.so - A shared library that implements the YottaDB run-time system, including the Call-In API. If Call-Ins are used from a standalone C/C++ program, this library needs to be explicitly linked into the program. See “Building Standalone Programs”, which describes the necessary linker options on each supported platforms.
* mumps - The YottaDB startup program that dynamically links with libgtmshr.so.
* libyottadb.h - A C-header file containing the declarations of Call-In API.

.. note::
   .so is the recognized shared library file extension on most UNIX platforms.

The following sections describe the files relevant to using Call-Ins.

**libyottadb.h**

The header file provides signatures of all Call-In interface functions and definitions of those valid data types that can be passed from C to M. YottaDB strongly recommends that these types be used instead of native types (int, char, float, and so on), to avoid possible mismatch problems during parameter passing.

libyottadb.h defines the following types that can be used in Call-Ins.

+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Type                  | Usage                                                                                                                                                        |
+=======================+==============================================================================================================================================================+
| void                  | Used to express that there is no function return value                                                                                                       |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ydb_int_t             | ydb_int_t has 32-bit length on all platforms.                                                                                                                |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ydb_uint_t            | ydb_uint_t has 32-bit length on all platforms                                                                                                                |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ydb_long_t            | ydb_long_t has 32-bit length on 32-bit platforms and 64-bit length on 64-bit platforms. It is much the same as the C language long type.                     |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ydb_ulong_t           | ydb_ulong_t is much the same as the C language unsigned long type.                                                                                           |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ydb_float_t           | floating point number                                                                                                                                        |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ydb_double_t          | Same as above but double precision.                                                                                                                          |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ydb_status_t          | type int. If it returns zero then the call was successful. If it is non-zero, when control returns to YottaDB, it issues a trappable error.                  |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ydb_long_t*           | Pointer to ydb_long_t. Good for returning integers.                                                                                                          |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+
| ydb_ulong_t*          | Pointer to ydb_ulong_t. Good for returning unsigned integers.                                                                                                |
+-----------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. parsed-literal::
   typedef struct {
       ydb_long_t length;
       ydb_char_t* address;
   } ydb_string_t;

The pointer types defined above are 32-bit addresses on all 32-bit platforms. For 64-bit platforms, ydb_string_t* is a 64-bit address.

libyottadb.h also provides an input-only parameter type ydb_pointertofunc_t that can be used to obtain call-back function pointers via parameters in the external routine. If a parameter is specified as I:ydb_pointertofunc_t and if a numeric value (between 0-5) is passed for this parameter in M, YottaDB interprets this value as the index into the callback table and passes the appropriate callback function pointer to the external routine.

.. note::
   YottaDB represents values that fit in 18 digits as numeric values, and values that require more than 18 digits as strings.

libyottadb.h also includes definitions for the following entry points exported from libgtmshr: 

.. parsed-literal::
   void ydb_hiber_start(ydb_uint_t mssleep);
   void ydb_hiber_start_wait_any(ydb_uint_t mssleep)
   void ydb_start_timer(ydb_tid_t tid, ydb_int_t time_to_expir, void (\*handler)(), ydb_int_t hdata_len, void \\*hdata);
   void ydb_cancel_timer(ydb_tid_t tid);

where:

* mssleep - milliseconds to sleep
* tid - unique timer id value
* time_to_expir - milliseconds until timer drives given handler
* handler - function pointer to handler to be driven
* hdata_len - 0 or length of data to pass to handler as a parameter
* hdata - NULL or address of data to pass to handler as a parameter

ydb_hiber_start() always sleeps until the time expires; ydb_hiber_start_wait_any() sleeps until the time expires or an interrupt by any signal (including another timer). ydb_start_timer() starts a timer but returns immediately (no sleeping) and drives the given handler when time expires unless the timer is canceled.

.. note::
   libyottadb.h continues to be upward compatible with gtmxc_types.h. gtmxc_types.h explicitly marks the xc_* equivalent types as deprecated.

**Call-In table**

The Call-In table file is a text file that contains the signatures of all M label references that get called from C. In order to pass the typed C arguments to the type-less M formallist, the environment variable ydb_ci must be defined to point to the Call-In table file path. Each signature must be specified separately in a single line. YottaDB reads this file and interprets each line according to the following convention (specifications within box brackets "[]", are optional):

.. parsed-literal::
   <c-call-name> : <ret-type> <label-ref> ([<direction>:<param-type>,...])

where,

<label-ref>: is the entry point (that is a valid label reference) at which YottaDB starts executing the M routine being called-in

<c-call-name>: is a unique C identifier that is actually used within C to refer to <label-ref>

<direction>: is either I (input-only), O (output-only), or IO (input-output)

<ret-type>: is the return type of <label-ref>

.. note::
   Since the return type is considered as an output-only (O) parameter, the only types allowed are pointer types and void. Void cannot be specified as parameter.

<param-type>: is a valid parameter type. Empty parentheses must be specified if no argument is passed to <label-ref>

The <direction> indicates the type of operation that YottaDB performs on the parameter read-only (I), write-only (O), or read-write (IO). All O and IO parameters must be passed by reference, that is, as pointers since YottaDB writes to these locations. All pointers that are being passed to YottaDB must be pre-allocated. The following table details valid type specifications for each direction.

+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
| Directions        | Allowed Parameter Types                                                                                                                     |
+===================+=============================================================================================================================================+
| I                 | ydb_long_t, ydb_ulong_t, ydb_float_t, ydb_double_t,_ydb_long_t*, ydb_ulong_t*, ydb_float_t*, ydb_double_t*,_ydb_char_t*, ydb_string_t*      |
+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------+
| O/IO              | ydb_long_t*, ydb_ulong_t*, ydb_float_t*, ydb_double_t*,_ydb_char_t*, ydb_string_t*                                                          |
+-------------------+---------------------------------------------------------------------------------------------------------------------------------------------+

Here is an example of Call-In table (calltab.ci) for piece.m (see “Example: Calling YottaDB from a C Program”):

.. parsed-literal::
   print     :void            display^piece()
   getpiece  :ydb_char_t*     get^piece(I:ydb_char_t*, I:ydb_char_t*, I:ydb_long_t)
   setpiece  :void            set^piece(IO:ydb_char_t*, I:ydb_char_t*, I:ydb_long_t, I:ydb_char_t*)
   pow       :ydb_double_t*   pow^piece(I:ydb_double_t, I:ydb_long_t)
   powequal  :void            powequal^piece(IO:ydb_double_t*, I:ydb_long_t)
   piece     :ydb_double_t*   pow^piece(I:ydb_double_t, I:ydb_long_t)

.. note::
   The same entryref can be called by different C call names (for example, pow, and piece). However, if there are multiple lines with the same call name, only the first entry will be used by YottaDB. YottaDB ignores all subsequent entries using a call name.

++++++++++++++++++++++++
Call-In Interface
++++++++++++++++++++++++

This section is further broken down into 6 subsections for an easy understanding of the Call-In interface. The section is concluded with an elaborate example.

**Initialize YottaDB**

.. parsed-literal::
   ydb_status_t ydb_init(void);

If the base program is not an M routine but a standalone C program, ydb_init() must be called (before calling any YottaDB functions), to initialize the YottaDB run-time system.

ydb_init() returns zero (0) on success. On failure, it returns the YottaDB error status code whose message can be read into a buffer by immediately calling ydb_zstatus(). Duplicate invocations of ydb_init() are ignored by YottaDB.

If Call-Ins are used from an external call function (that is, a C function that has itself been called from M code), ydb_init() is not needed, because YottaDB is initialized before the External Call. All ydb_init() calls from External Calls functions are ignored by YottaDB.

**Call an M Routine from C**

YottaDB provides 2 interfaces for calling a M routine from C. These are:

* ydb_cip
* ydb_ci

ydb_cip offers better performance on calls after the first one. 

**ydb_cip**

.. parsed-literal::
   ydb_status_t ydb_cip(ci_name_descriptor \*ci_info, ...);

The variable argument function ydb_cip() is the interface that invokes the specified M routine and returns the results via parameters.

ci_name_descriptor has the following structure:

.. parsed-literal::
   typedef struct
   {
     ydb_string_t rtn_name;
     void* handle;
   } ci_name_descriptor;

rtn_name is a C character string indicating the corresponding <lab-ref> entry in the Call-In table.

The handle is YottaDB private information initialized by YottaDB on the first call-in and to be provided unmodified to YottaDB on subsequent calls. If application code modifies it, it will corrupt the address space of the process, and potentially cause just about any bad behavior that it is possible for the process to cause, including but not limited to process death, database damage and security violations.

The ydb_cip() call must follow the following format:

.. parsed-literal::
   status = ydb_cip(<ci_name_descriptor> [, ret_val] [, arg1] ...);

First argument: ci_name_descriptor, a null-terminated C character string indicating the alias name for the corresponding <lab-ref> entry in the Call-In table.

Optional second argument: ret_val, a pre-allocated pointer through which YottaDB returns the value of QUIT argument from the (extrinsic) M routine. ret_val must be the same type as specified for <ret-type> in the Call-In table entry. The ret_val argument is needed if and only if <ret-type> is not void.

Optional list of arguments to be passed to the M routine's formallist: the number of arguments and the type of each argument must match the number of parameters, and parameter types specified in the corresponding Call-In table entry. All pointer arguments must be pre-allocated. YottaDB assumes that any pointer, which is passed for O/IO-parameter points to valid write-able memory.

The status value returned by ydb_cip() indicates the YottaDB status code; zero (0), if successful, or a non-zero; $ZSTATUS error code on failure. The $ZSTATUS message of the failure can be read into a buffer by immediately calling ydb_zstatus().

**ydb_ci**

.. parsed-literal::
   ydb_status_t ydb_ci(const ydb_char_t* c_call_name, ...);

The variable argument function ydb_ci() is the interface that actually invokes the specified M routine and returns the results via parameters. The ydb_ci() call must be in the following format:

.. parsed-literal::
   status = ydb_ci(<c_call_name> [, ret_val] [, arg1] ...);

First argument: c_call_name, a null-terminated C character string indicating the alias name for the corresponding <lab-ref> entry in the Call-In table.

Optional second argument: ret_val, a pre-allocated pointer through which YottaDB returns the value of QUIT argument from the (extrinsic) M routine. ret_val must be the same type as specified for <ret-type> in the Call-In table entry. The ret_val argument is needed if and only if <ret-type> is not void.

Optional list of arguments to be passed to the M routine's formallist: the number of arguments and the type of each argument must match the number of parameters, and parameter types specified in the corresponding Call-In table entry. All pointer arguments must be pre-allocated. YottaDB assumes that any pointer, which is passed for O/IO-parameter points to valid write-able memory.

The status value returned by ydb_ci() indicates the YottaDB status code; zero (0), if successful, or a non-zero; $ZSTATUS error code on failure. The $ZSTATUS message of the failure can be read into a buffer by immediately calling ydb_zstatus(). For more details, see “Print Error Messages”.

**Example: Calling YottaDB from a C Program**

Here are some working examples of C programs that use call-ins to invoke YottaDB. Each example is packaged in a zip file which contains a C program, a call-in table, and a YottaDB API. To run an example, download and follow the compiling and linking instructions in the comments of the C program.

+--------------------------------+----------------------------------------------------------------------------------------------+
| Example                        | Download Information                                                                         |
+================================+==============================================================================================+
| gtmaccess.c (ydb_ci interface) | https://gitlab.com/YottaDB/DB/YDBDoc/blob/master/ProgGuide/gtmci_gtmaccess.zip               |
+--------------------------------+----------------------------------------------------------------------------------------------+
| gtmaccess.c (ydb_cip interface)| https://gitlab.com/YottaDB/DB/YDBDoc/blob/master/ProgGuide/gtmcip_gtmaccess.zip              |
+--------------------------------+----------------------------------------------------------------------------------------------+
| cpiece.c (ydb_ci interface)    | https://gitlab.com/YottaDB/DB/YDBDoc/blob/master/ProgGuide/gtmci_cpiece.zip                  |
+--------------------------------+----------------------------------------------------------------------------------------------+

**Print Error Messages**

.. parsed-literal::
   void ydb_zstatus (ydb_char_t* msg_buffer, ydb_long_t buf_len);

This function returns the null-terminated $ZSTATUS message of the last failure via the buffer pointed by msg_buffer of size buf_len. The message is truncated to size buf_len if it does not fit into the buffer. ydb_zstatus() is useful if the external application needs the text message corresponding to the last YottaDB failure. A buffer of 2048 is sufficient to fit in any YottaDB message.

**Exit from YottaDB**

.. parsed-literal::
   ydb_status_t  ydb_exit (void);

ydb_exit() can be used to shut down all databases and exit from the YottaDB environment that was created by a previous ydb_init().

Note that ydb_init() creates various YottaDB resources and keeps them open across multiple invocations of ydb_ci() until ydb_exit() is called to close all such resources. On successful exit, ydb_exit() returns zero (0), else it returns the $ZSTATUS error code.

ydb_exit() cannot be called from an external call function. YottaDB reports the error YDB-E-INVGTMEXIT if an external call function invokes ydb_exit(). Since the YottaDB run-time system must be operational even after the external call function returns, ydb_exit() is meant to be called only once during a process lifetime, and only from the base C/C++ program when YottaDB functions are no longer required by the program.

+++++++++++++++++++++++++++++
Building Standalone Programs
+++++++++++++++++++++++++++++

All external C functions that use call-ins should include the header file libyottadb.h that defines various types and provides signatures of call-in functions. To avoid potential size mismatches with the parameter types, YottaDB strongly recommends that gtm \*t types defined in libyottadb.h be used instead of the native types (int, float, char, etc).

To use call-ins from a standalone C program, it is necessary that the YottaDB runtime library (libgtmshr.so) is explicitly linked into the program. If call-ins are used from an External Call function (which in turn was called from YottaDB through the existing external call mechanism), the External Call library does not need to be linked explicitly with libgtmshr.so since YottaDB would have already loaded it.

The following sections describe compiler and linker options that must be used on each platform for call-ins to work from a standalone C/C++ program. 

**IBM pSeries (RS/6000) AIX**

* Compiler: -I$ydb_dist
* Linker: -L$ydb_dist -lgtmshr

**X86 GNU/Linux**

* Compiler: -I$ydb_dist
* Linker: -L$ydb_dist -lgtmshr -rpath $ydb_dist
* YottaDB advises that the C/C++ compiler front-end be used as the Linker to avoid specifying the system startup routines on the ld command. The compile can pass linker options to ld using -W option (for example, cc -W1, -R, $ydb_dist). For more details on these options, refer to the appropriate system's manual on the respective platforms.

++++++++++++++++++++++++++++++
Nested Call-Ins
++++++++++++++++++++++++++++++

Call-ins can be nested by making an external call function in-turn call back into YottaDB. Each ydb_ci() called from an External Call library creates a call-in base frame at $ZLEVEL 1 and executes the M routine at $ZLEVEL 2. The nested call-in stack unwinds automatically when the External Call function returns to YottaDB.

YottaDB currently allows up to 10 levels of nesting, if TP is not used, and less than 10 if YottaDB supports call-ins from a transaction (see “Rules to Follow in Call-Ins”). YottaDB reports the error YDB-E-CIMAXLEVELS when the nesting reaches its limit.

Following are the YottaDB commands, Intrinsic Special Variables, and functions whose behavior changes in the context of every new nested call-in environment.

ZGOTO operates only within the current nested M stack. ZGOTO zero (0) unwinds all frames in the current nested call-in M stack (including the call-in base frame) and returns to C. ZGOTO one (1) unwinds all current stack frame levels up to (but not inclusive) the call-in base frame and returns to C, while keeping the current nested call-in environment active for any following ydb_ci() calls.

$ZTRAP/$ETRAP NEW'd at level 1 (in GTM$CI frame).

$ZLEVEL initializes to one (1) in GTM$CI frame, and increments for every new stack level.

$STACK initializes to zero (0) in GTM$CI frame, and increments for every new stack level.

$ESTACK NEW'd at level one (1) in GTM$CI frame.

$ECODE/$STACK() initialized to null at level one (1) in GTM$CI frame.

.. note::
   After a nested call-in environment exits and the external call C function returns to M, the above ISVs and Functions restore their old values.

++++++++++++++++++++++++++++++++++++
Rules to Follow in Call-Ins
++++++++++++++++++++++++++++++++++++

1. External calls must not be fenced with TSTART/TCOMMIT if the external routine calls back into mumps using the call-in mechanism.
2. The external application should never call exit() unless it has called ydb_exit() previously. YottaDB internally installs an exit handler that should never be bypassed.
3. The external application should never use any signals when YottaDB is active since YottaDB reserves them for its internal use. YottaDB provides the ability to handle SIGUSR1 within M (see “$ZINTerrupt” for more information). An interface is provided by YottaDB for timers. Although not required, YottaDB recommends the use of ydb_malloc() and ydb_free() for memory management by C code that executes in a YottaDB process space for enhanced performance and improved debugging.
4. YottaDB performs device input using the read() system service. UNIX documentation recommends against mixing this type of input with buffered input services in the fgets() family and ignoring this recommendation is likely to cause a loss of input that is difficult to diagnose and understand.

--------------------------------------
Type Limits for Call-Ins and Call-Outs
--------------------------------------

Depending on the direction (I, O, or IO) of a particular type, both call-ins and call-outs may transfer a value in two directions as follows:

.. parsed-literal::
   Call-out: YottaDB -> C -> YottaDB       Call-in:     C -> YottaDB -> C
               |        |       |                        |      |       |
               '--------'-------'                        '------'-------'
                  1     2                                   2     1

In the following table, the YottaDB->C limit applies to 1 and the C->YottaDB limit applies to 2. In other words, YottaDB->C applies to I direction for call-outs and O direction for call-ins and C->YottaDB applies to I direction for call-ins and O direction for call-outs.

+----------------------------------------------------------------------------------+-------------------------------------------------------------------+----------------------------------------------------------------------+
|                                                                                  | YottaDB->C                                                        | C->YottaDB                                                           |
+==================================================================================+====================+==============================================+============================+=========================================+
| **Type**                                                                         | **Precision**      | **Range**                                    | **Precision**              | **Range**                               |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_int_t, ydb_int_t *                                                           | Full               | [-2^31+1, 2^31-1]                            | Full                       | [-2^31, 2^31-1]                         |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_uint_t, ydb_uint_t *                                                         | Full               | [0, 2^32-1]                                  | Full                       | [0, 2^32-1]                             |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_long_t, ydb_long_t * (64-bit)                                                | 18 digits          | [-2^63+1, 2^63-1]                            | 18 digits                  | [-2^63, 2^63-1]                         |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_long_t, ydb_long_t * (32-bit)                                                | Full               | [-2^31+1, 2^31-1]                            | Full                       | [-2^31, 2^31-1]                         |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_ulong_t, ydb_ulong_t * (64-bit)                                              | 18 digits          | [0, 2^64-1]                                  | 18 digits                  | [0, 2^64-1]                             |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_ulong_t, ydb_ulong_t * (32-bit)                                              | Full               | [0, 2^32-1]                                  | Full                       | [0, 2^32-1]                             |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_float_t, ydb_float_t *                                                       | 6-9 digits         | [1E-43, 3.4028235E38]                        | 6 digits                   | [1E-43, 3.4028235E38]                   |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_double_t, ydb_double_t *                                                     | 15-17 digits       | [1E-43, 1E47]                                | 15 digits                  | [1E-43, 1E47]                           |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_char_t *                                                                     | N/A                | ["", 1MiB]                                   | N/A                        | ["", 1MiB]                              |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_char_t **                                                                    | N/A                | ["", 1MiB]                                   | N/A                        | ["", 1MiB]                              |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+
| ydb_string_t *                                                                   | N/A                | ["", 1MiB]                                   | N/A                        | ["", 1MiB]                              |
+----------------------------------------------------------------------------------+--------------------+----------------------------------------------+----------------------------+-----------------------------------------+

.. note::
   ydb_char_t ** is not supported for call-ins but they are included for IO and O direction usage with call-outs. For call-out use of ydb_char_t \* and ydb_string_t \*, the specification in the interface definition for preallocation sets the range for IO and O, with a maximum of 1MiB.

----------------------------------
YottaDB Java Interface Plug-In
----------------------------------

YDBJava provides a mechanism to call-in to YDB from Java application code, and to call out from YottaDB to Java application code. YDBJava is supported on Linux on x86 and x86_64, AIX, and Solaris on SPARC. The following table lists the platforms and Java distributions on which YottaDB tested the YDBJava plug-in. Although YDBJava may work on other combinations of platforms and Java implementations, the platforms on which YDBJava is tested are below. 

+--------------------+---------------------------------+
| OS                 | Java                            |
+====================+=================================+
| IBM System p AIX   | IBM JDK 1.7                     |
+--------------------+---------------------------------+
| Sun SPARC Solaris  | Oracle JDK 1.6                  |
+--------------------+---------------------------------+
| x86_64 GNU/Linux   | OpenJDK 1.6 and 1.7             |
+--------------------+---------------------------------+
| x86 GNU/Linux      | OpenJDK 1.6 and 1.7             |
+--------------------+---------------------------------+

++++++++++++++++
Installation
++++++++++++++++

YDBJava comes with a Makefile that you can use with GNU make to build, test, install, and uninstall the package. On some platforms, GNU make may be accessed with the command gmake, not make. You can build and test YDBJava as a normal (non-root) user and then as root, install it as a YottaDB plug-in. The targets in the Makefile that are intended for external use are:

* all: creates libgtmj2m.so and libgtmm2j.so (shared libraries of C code that acts as a gateway for Java call-ins and call-outs, respectively) and gtmji.jar (a Java archive containing YDBJava type wrapper and thread management classes).
* clean: deletes all files created as a result of running the test and/or all target.
* install: executed as root, installs YDBJava as a plug-in under the YottaDB installation directory.
* install-test: executed as root, ensures the operation of YDBJava after building and installation. Messages "GTMJI-INSTALL-SUCCESS: Call-ins test succeeded." and "GTMJI-INSTALL-SUCCESS: Call-outs test succeeded." confirm successful installation. If you are using UTF-8, make sure to set the environment; two additional GTMJI-INSTALL-SUCCESS messages should be printed.
* test: ensures the operation of YDBJava after building and before installation. As with the install-test target, "GTMJI-INSTALL-SUCCESS: Call-ins test succeeded." and "GTMJI-INSTALL-SUCCESS: Call-outs test succeeded." messages should appear. If you are using UTF-8, make sure to set the environment; two additional GTMJI-INSTALL-SUCCESS messages should be printed.
* uninstall: executed as root, removes the installed plug-in from under the YottaDB installation directory.

The following targets also exist but are intended for use within the Makefile rather than for external invocation: libgtmj2m.so, libgtmm2j.so, gtmji.jar, $(PLUGINDIR)/libgtmj2m.so, $(PLUGINDIR)/libgtmm2j.so, $(PLUGINDIR)/gtmji.jar, $(UTFPLUGINDIR)/libgtmj2m.so, $(UTFPLUGINDIR)/libgtmm2j.so, and $(UTFPLUGINDIR)/gtmji.jar.

To run the Makefile, set the following environment variables:

* ydb_dist: Installation directory of YottaDB that contains libyottadb.so and such include files as gtm_common_defs.h and gtmxc_types.h. If you plan to install YDBJava for multiple YottaDB versions, please clean the build each time, since both gtmxc_types.h and gtm_common_defs.h are included from $ydb_dist to build the shared library.

* JAVA_HOME: Top directory of your Java installation, such as /usr/lib/jvm/jdk1.6.0_25.

* JAVA_SO_HOME: Directory that contains libjava.so; typically,

  -  AIX: $JAVA_HOME/jre/lib/ppc64
  -  Linux: $JAVA_HOME/jre/lib/amd64, $JAVA_HOME/jre/lib/i386, or $JAVA_HOME/jre/lib/i686
  -  Solaris: $JAVA_HOME/jre/lib/sparcv9

* JVM_SO_HOME: Directory that contains libjvm.so; typically,

   - AIX: $JAVA_HOME/jre/lib/ppc64/j9vm
   - Linux: $JAVA_HOME/jre/lib/amd64/server, $JAVA_HOME/jre/lib/i386/server, or $JAVA_HOME/jre/lib/i686/server
   - Solaris: $JAVA_HOME/jre/lib/sparcv9/server

Note that if you also have a YottaDB installation with UTF-8 support (that is, YottaDB executables under $ydb_dist/utf8), then you might need to configure a few additional environment variables for targets that run YDBJava tests, such as test and install-test. Setting ydb_icu_version suffices in most situations.

The steps for a typical YDBJava installation are as follows:

* Set ydb_dist, JAVA_HOME, JAVA_SO_HOME, and JVM_SO_HOME environment variables.
* Run :code:`make all`.
* Run :code:`make test`. When make test completes, two (four if you have a UTF-8-enabled installation) "GTMJI-INSTALL-SUCCESS ..." messages get displayed.
* Run :code:`make install`.
* Run :code:`make install-test`. When :code:`make install-test` completes, two (four if you have a UTF-8-enabled installation) "GTMJI-INSTALL-SUCCESS ..." messages get displayed.
* Run :code:`make clean` to remove all temporary YDBJava files created in the current directory by other make commands. 

++++++++++++++++++++++++++++++
YDB Call-Ins Usage from Java
++++++++++++++++++++++++++++++

**Environment Configuration**

To call-in to YottaDB application code from Java application code requires the gtmji.jar Java archive together with the libgtmj2m.so shared library. The JAR contains the definitions of special types that the call-in functions may use for arguments; it also loads the shared library, performs concurrency control, and sets up proper rundown logic on Java process termination. In addition to the usual YottaDB environment variables, such as ydb_routines and ydb_gbldir, the following environment variables need to be defined:

* ydb_ci: The location of the call-in table.
* LD_LIBRARY_PATH (LIBPATH on AIX): Includes the location of libgtmj2m.so shared library, such as /usr/local/lib/yottadb/r122/plugin. Alternatively, pass the location of the shared library to the JVM via java.library.path property.

After setting these environment variables, the invocation of a Java process might look like:

.. parsed-literal::
   java -classpath "/path/to/classes/top/dir/:/path/to/gtmji.jar" com.callins.Test

or

.. parsed-literal::
   java -Djava.library.path=/path/to/libgtmj2m/dir/ -classpath "/path/to/classes/top/dir/:/path/to/gtmji.jar" com.callins.Test

in case you do not set LD_LIBRARY_PATH.

It is also possible to define the CLASSPATH environment variable instead of specifying the -classpath option.

**Invocations**

YDBJava provides the following methods for invoking M routines, each for a specific return type:

.. parsed-literal::
   public static native void doVoidJob(String routine, Object... args);     
   public static native int doIntJob(String routine, Object... args);     
   public static native long doLongJob(String routine, Object... args);     
   public static native float doFloatJob(String routine, Object... args);     
   public static native double doDoubleJob(String routine, Object... args);     
   public static native String doStringJob(String routine, Object... args);     
   public static native byte[] doByteArrayJob(String routine, Object... args);

These functions are defined in the GTMCI class; so, after importing gtmji.jar, the call-in invocations have the following format:

.. parsed-literal::
   GTMCI.doXXXJob(routineName, arg1, arg2, ...);

In many ways, these functions are similar to ydb_ci() and ydb_cip() calls from C. Note, however, that unlike with C, you do not have to call the initialization and rundown functions explicitly from Java because YDBJava handles these operations automatically. Another key difference from C concerns Java's inability to modify primitive types by reference. To address this shortcoming, YDBJava provides the following wrapper classes to the five respective primitives:

* GTMBoolean
* GTMInteger
* GTMLong
* GTMFloat
* GTMDouble

Although Strings are object types in Java, they are immutable and do not require a direct call to a constructor at instantiation. As a result, YDBJava provides String-type arguments with call-in invocations, but such calls do not modify the argument's content even if that argument is declared for input-output use in the mapping table (see below). To pass strings that can be modified, the plug-in implements the GTMString wrapper. Similarly, although YottaDB application code can modify the contents of a byte array argument, it cannot expand or reduce its size. Modifying a byte[] argument passed from Java does not alter the array's original capacity; furthermore, if the modifications target fewer elements than the array contains, the unmodified elements retain their values. In contrast, GTMByteArray arguments expand when a newly assigned value exceeds the original capacity of the array; still, if a newly assigned value is smaller than the original size, the unmodified bytes retain their original contents.

**Types**

YDBJava provides the following types for calling in to YottaDB from Java:

* GTMBoolean
* GTMInteger
* GTMLong
* GTMFloat
* GTMDouble
* GTMString
* GTMByteArray
* String
* byte[]
* BigDecimal

Each class contains a 'value' field of the corresponding primitive or object (in case of GTMString) type. For simplicity and performance reasons, the field is public, and there are no mutator or accessor methods to access it. Nevertheless, you can print the actual values without explicitly dereferencing the field because the GTM-XXX classes implement the toString() method.

Because Java always passes objects by reference, YDBJava only allows a call-in function to modify its arguments when they are marked as input-output or output-only (as opposed to input-only) in the call-in table. From a programmer's point of view, passing input-only and input-output arguments is identical. Once again, bear in mind that it is NOT possible to modify Strings even if you mark them for input-output use: if you need to modify Strings, use GTMStrings. The table below summarizes the proper usage of all types allowed with YottaDB call-ins from Java:

+------------------------+------------------------------------+-------------------+
| Type in Java           | Type in CI Table                   | Use               |
+========================+====================================+===================+
| GTMBoolean             | gtm_jboolean_t                     | I, IO, O          |
+------------------------+------------------------------------+-------------------+
| GTMInteger             | gtm_jint_t                         | I, IO, O          |
+------------------------+------------------------------------+-------------------+
| GTMLong                | gtm_jlong_t                        | I, IO, O          |
+------------------------+------------------------------------+-------------------+
| GTMFloat               | gtm_jfloat_t                       | I, IO, O          |
+------------------------+------------------------------------+-------------------+
| GTMDouble              | gtm_jdouble_t                      | I, IO, O          |
+------------------------+------------------------------------+-------------------+
| GTMString              | gtm_jstring_t                      | I, IO, O          |
+------------------------+------------------------------------+-------------------+
| GTMByteArray           | gtm_jbyte_array_t                  | I, IO, O          |
+------------------------+------------------------------------+-------------------+
| String                 | gtm_jstring_t                      | I                 |
+------------------------+------------------------------------+-------------------+
| byte[]                 | gtm_jbyte_array_t                  | I, IO, O          |
+------------------------+------------------------------------+-------------------+
| BigDecimal             | gtm_jbig_decimal_t                 | I                 |
+------------------------+------------------------------------+-------------------+

Notice the special gtm_jXXX_t mapping types defined for usage with Java; be sure to employ them instead of the ydb_XXX_t and ydb_XXX_t * types designated for usage with C. To utilize an argument in the input or output direction, it suffices to correctly label it as 'I', 'O', or 'IO'; do not include '*' as the Java programming language does not have any close analog to the pointer types in C/C++.

Do not pass a variable of any other type than described above to a call-in function from Java. The total number of arguments should not exceed 32.

**Return Types**

Whenever the call-in routine is expected to return a value, use the corresponding ydb_ci function. Unlike with C, do not insert additional parameters to retrieve the return value. Specify one of the available return types — void, int, long, float, double, String, or byte[] — in the call-in table. 

**Input vs Input/Output Arguments**

All input/output call-in arguments are passed to YottaDB by reference. The ZWRITE and ZSHOW output formats of such arguments appear to have an association ("; \*") with a non-existing alias variable, but under most conditions they behave just like local variables. One exception is the difference in operation of KILL and KILL * commands. While KILL * only removes input/output arguments, KILL removes all arguments regardless of type. Arguments removed by either KILL or KILL * become undefined in YottaDB, yet any modifications to the arguments made prior to KILL * reflect on the Java side, whereas KILL clears all YottaDB modifications.

**String Conversion**

YDBJava converts all String and GTMString arguments from the UTF-16 encoding used by Java to UTF-8 before passing them to YottaDB. Additionally, in case of input-output or output-only GTMStrings, the plug-in converts the UTF-8 values back to UTF-16 during the transfer from M to Java. Unless you are assured that the application only deals with ASCII characters ($Char(0) through $Char(127)), YottaDB must run in UTF-8 mode. Use byte[] and GTMByteArray arguments for data such as binary values, that you want to pass unmodified between Java and GT.M.

**Exceptions**

Whenever YottaDB detects an error condition with a call-in—whether in the invocation processing or the M program execution—it returns control to Java, which throws an exception with a descriptive error message . It is the responsibility of Java application code to catch and handle the exception.

**Multi-Threading**

Java applications normally expect to run multi-threaded, but the YottaDB runtime system is single-threaded. YDBJava therefore, ensures that only one thread executes YottaDB code at any given time; any additional thread that attempts to enter the YottaDB runtime system is blocked until the first thread returns to the control of the Java runtime system.

To avoid unpredictable results, Java application code should always protect the arguments used when calling into YottaDB from unsynchronized reads and writes to prevent thread synchronization issues. If an M routine modifies one of its arguments inside a call-in while some other thread tries to read it, or if M reads an argument which might be modified in a different thread, application code needs to ensure correct synchronization between both read and write threads.

As YottaDB reserves the right to make the YottaDB runtime system multi-threaded at a future date, you should ensure that your application code does not rely on the single-threadedness of the YottaDB runtime system. Also, while M local variables are shared by all Java threads that call into M, this behavior may or may not continue if and when YottaDB makes the runtime system multi-threaded in the future.

**Examples**

Consider the following example. The call-in table contains two entries:

.. parsed-literal::
   f1:gtm_jdouble_t ci1^rtns(I:gtm_jboolean_t,I:gtm_jstring_t,I:gtm_jbyte_array_t,I:gtm_jbig_decimal_t)        
   f2:void ci2^rtns(IO:gtm_jint_t,IO:gtm_jlong_t,IO:gtm_jfloat_t,IO:gtm_jstring_t,IO:gtm_jbyte_array_t)

The first entry exposes the 'ci1' label from the 'rtns' routine to Java under the name 'f1'; the second entry exposes the 'ci2' label from the 'rtns' routine to Java under the name 'f2'. The first function returns a double value and expects four arguments of types GTMBoolean, String or GTMString, byte[] or GTMByteArray, and BigDecimal, respectively. The second function does not return a value and expects five arguments of types GTMInteger, GTMLong, GTMFloat, String or GTMString, and byte[] or GTMByteArray, respectively.

The 'rtns' routine contains the following:

.. parsed-literal::
   ci1(bi,jsi,gbai,bdi)       
     write "Inside c1:",!       
     write "bi: "_bi,!,"jsi: "_jsi,!,"gbai: "_gbai,!,"bdi: "_bdi,!       
     write "----------------------",!       
     set bi=1,jsi=2,gbai=3,bdi=4       
     quit 5.678       
       
   ci2(iio,lio,fio,gsio,jbaio)       
     write "Inside c2:",!       
     write "iio: "_iio,!,"lio: "_lio,!,"fio: "_fio,!,"gsio: "_gsio,!,"jbaio: "_jbaio,!       
     write "----------------------",!       
     set iio=123,lio=234,fio=345,gsio="567",jbaio=$char(54)_$char(55)_$char(56)       
     quit

Finally, the Java class that invokes the call-in looks like:

.. parsed-literal::
   package com.fis.test;  
  
   import java.math.BigDecimal;  
  
   import com.fis.gtm.ji.GTMBoolean;  
   import com.fis.gtm.ji.GTMByteArray;  
   import com.fis.gtm.ji.GTMCI;  
   import com.fis.gtm.ji.GTMDouble;  
   import com.fis.gtm.ji.GTMFloat;  
   import com.fis.gtm.ji.GTMInteger;  
   import com.fis.gtm.ji.GTMLong;  
   import com.fis.gtm.ji.GTMString;  
  
   public class CI {  
  
     public static void main(String[] args) {  
       try {  
         boolean booleanValue = false;  
         int intValue = 3;  
         long longValue = 3141L;  
         float floatValue = 3.141f;  
         double doubleValue = 3.1415926535;  
         String gtmStringValue = "GT.M String Value";  
         String javaStringValue = "Java String Value";  
         String gtmByteArrayValue = new String(new byte[]{51, 49, 52, 49});  
         String javaByteArrayValue = new String(new byte[]{51, 49, 52, 50});  
         String bigDecimalValue = "3.14159265358979323846";  
  
         GTMBoolean gtmBoolean = new GTMBoolean(booleanValue);  
         GTMInteger gtmInteger = new GTMInteger(intValue);  
         GTMLong gtmLong = new GTMLong(longValue);  
         GTMFloat gtmFloat = new GTMFloat(floatValue);  
         GTMDouble gtmDouble = new GTMDouble(doubleValue);  
         GTMString gtmString = new GTMString(gtmStringValue);  
         GTMByteArray gtmByteArray = new GTMByteArray(gtmByteArrayValue.getBytes());  
         String javaString = javaStringValue;  
         byte[] javaByteArray = javaByteArrayValue.getBytes();  
         BigDecimal bigDecimal = new BigDecimal(bigDecimalValue);  
  
         System.out.println(  
           "Before f1 and f2:\n" +  
           "gtmBoolean: " + gtmBoolean + "\n" +  
           "gtmInteger: " + gtmInteger + "\n" +  
           "gtmLong: " + gtmLong + "\n" +  
           "gtmFloat: " + gtmFloat + "\n" +  
           "gtmDouble: " + gtmDouble + "\n" +  
           "gtmString: " + gtmString + "\n" +  
           "gtmByteArray: " + gtmByteArray + "\n" +  
           "javaString: " + javaString + "\n" +  
           "javaByteArray: " + new String(javaByteArray) + "\n" +  
           "bigDecimal: " + bigDecimal + "\n" +  
           "----------------------");  
  
         double doubleReturnValue = GTMCI.doDoubleJob(  
           "f1",  
           gtmBoolean,  
           javaString,  
           gtmByteArray,  
           bigDecimal);  
  
         Thread.sleep(1000); // for synchronization of the output  
  
         System.out.println(  
           "After f1 but before f2:\n" +  
           "gtmBoolean: " + gtmBoolean + "\n" +  
           "gtmInteger: " + gtmInteger + "\n" +  
           "gtmLong: " + gtmLong + "\n" +  
           "gtmFloat: " + gtmFloat + "\n" +  
           "gtmDouble: " + gtmDouble + "\n" +  
           "gtmString: " + gtmString + "\n" +  
           "gtmByteArray: " + gtmByteArray + "\n" +  
           "javaString: " + javaString + "\n" +  
           "javaByteArray: " + new String(javaByteArray) + "\n" +  
           "bigDecimal: " + bigDecimal + "\n" +  
           "doubleReturnValue: " + doubleReturnValue + "\n" +  
           "----------------------");  
  
         GTMCI.doVoidJob(  
           "f2",  
           gtmInteger,  
           gtmLong,  
           gtmFloat,  
           gtmString,  
           javaByteArray);  
  
         Thread.sleep(1000); // for synchronization of the output  
  
         System.out.println(  
           "After f1 and f2:\n" +  
           "gtmBoolean: " + gtmBoolean + "\n" +  
           "gtmInteger: " + gtmInteger + "\n" +  
           "gtmLong: " + gtmLong + "\n" +  
           "gtmFloat: " + gtmFloat + "\n" +  
           "gtmDouble: " + gtmDouble + "\n" +  
           "gtmString: " + gtmString + "\n" +  
           "gtmByteArray: " + gtmByteArray + "\n" +  
           "javaString: " + javaString + "\n" +  
           "javaByteArray: " + new String(javaByteArray) + "\n" +  
           "bigDecimal: " + bigDecimal + "\n");  
       } catch (Exception e) {  
         e.printStackTrace();  
       }     
     }  
   }

If correctly configured, the execution of the above class produces the following output:

.. parsed-literal::
   Before f1 and f2:      
   gtmBoolean: false      
   gtmInteger: 3      
   gtmLong: 3141      
   gtmFloat: 3.141      
   gtmDouble: 3.1415926535      
   gtmString: YottaDB String Value      
   gtmByteArray: 3141      
   javaString: Java String Value      
   javaByteArray: 3142      
   bigDecimal: 3.14159265358979323846      
   ----------------------      
   Inside c1:      
   bi: 0      
   jsi: Java String Value      
   gbai: 3141      
   bdi: 3.14159265358979323846      
   ----------------------      
   After f1 but before f2:      
   gtmBoolean: false      
   gtmInteger: 3      
   gtmLong: 3141      
   gtmFloat: 3.141      
   gtmDouble: 3.1415926535      
   gtmString: YottaDB String Value      
   gtmByteArray: 3141      
   javaString: Java String Value      
   javaByteArray: 3142      
   bigDecimal: 3.14159265358979323846      
   doubleReturnValue: 5.678      
   ----------------------      
   Inside c2:      
   iio: 3      
   lio: 3141      
   fio: 3.141      
   gsio: YottaDB String Value      
   jbaio: 3142      
   ----------------------      
   After f1 and f2:      
   gtmBoolean: false      
   gtmInteger: 123      
   gtmLong: 234      
   gtmFloat: 345.0      
   gtmDouble: 3.1415926535      
   gtmString: 567      
   gtmByteArray: 3141      
   javaString: Java String Value      
   javaByteArray: 6782      
   bigDecimal: 3.14159265358979323846

Notice that although there is an attempt to modify the arguments inside the 'ci1' function, they remain unchanged after the GTMCI.doDoubleJob("f1", ...) call. However, the values change in 'ci2', as seen after the GTMCI.doVoidJob("f2", ...) call. Note that the fourth byte of the javaByteArray argument preserved its value (because the call only changed three bytes).

++++++++++++++++++++++++++++++++++++++
YottaDB Call-Outs Usage with Java
++++++++++++++++++++++++++++++++++++++

**Environment Configuration**

To invoke Java programs from M code via the YottaDB call-out interface, the first line of the external call table should point to the libgtmm2j.so shared library. Java code must include the gtmji.jar Java archive to provide the special types for argument passing. Besides ydb_routines and ydb_gbldir, define the following environment variables:

* GTMXC_XXX: Includes the location of the call-out table definition, where XXX is the name of the external package as it is referenced in an M routine.
* GTMXC_classpath: Includes the top directory of the class file, or the JAR file with it, as well as the path to gtmji.jar. Please note that JAR paths should include the file name in the path.
* LD_LIBRARY_PATH (LIBPATH on AIX): Points to the locations of libgtmm2j.so, libjvm.so, and libjava.so shared libraries. (Use ':' as a delimeter.)
* LD_PRELOAD (LDR_PRELOAD64 on AIX): Points to the location of libjsig.so shared library (required for signal chaining).

By default YDBJava starts a JVM with the following flags:

* -Xrs: Reduces signal usage by the virtual machine.
* -Dgtm.callouts=1: Indicates Java call-out context for the GTMCI class within gtmji.jar in case of embedded Java call-in.
* -Djava.class.path=<GTMXC_classpath environment variable>: Sets the location of Java classes referenced by the program.

To specify additional JVM options (up to 50 total), initialize GTMXC_jvm_options environment variable, using ' ' or '|' as delimiter. A sample GTMXC_jvm_options string might look like:

.. parsed-literal::
   -Dspecial.value1=123 -Dspecial.value2=456 -Dspecial.value3=789

Duplicates of the default flags (-Xrs and -Djava.class.path) and unrecognized JVM options are omitted.

**Invocations**

Invocation of Java classes from M is similar to that of C shared libraries, except that the first parameter specifies the full class package path (with '/' instead of '.' as package delimiter), and the second parameter specifies the method name. Note that YDBJava only supports call-outs to static Java methods ) For example, to invoke a static long method doSomeWork from class WorkFactory in package com.abc.factory, use the following M code:

.. parsed-literal::
   set result=$&work.doSomeWork("com/abc/factoryWorkFactory","doSomeWork",firstParm,.secondParm)

The corresponding call-out table definition (named work.co) might look like this:

.. parsed-literal::
   /usr/local/lib/yottadb/r122/plugin/libgtmm2j.so  
   doSomeWork: gtm_jlong_t gtm_xcj(I:gtm_jboolean_t,IO:gtm_jdouble_t

Notice that the name of the method that doSomeWork maps to is gtm_xcj; always use the gtm_xcj method mapping in the call-out table when you work with Java classes. Do not list the class package and the method name in the call-out entry. The Java method referred to in the above example might be implemented as follows:

.. parsed-literal::
   public static long doSomeWork(Object[] args)   
   {  
     GTMBoolean b = (GTMBoolean)args[0];  
     GTMDouble d = (GTMDouble)args[1];  
     // do some work here  
     
     d.value = 5.358979; // this arg is IO and will be propagated back to M  
     return 123;  
   }

As with doSomeWork, the invoked Java method's only argument should be of Object[] type; individual arguments need to be cast to the expected types, as defined in the call-out table.

**Types**

With the exception of BigDecimal, the types that YottaDB provides for calling out to Java are the same as for calling in from Java: GTMBoolean, GTMInteger, GTMLong, GTMFloat, GTMDouble, GTMString, String, and byte[]. When passing an input-output or output-only argument from M, a '.' in front of the name indicates passing by reference, per standard M syntax. String or byte-array arguments are passed to Java as native types (that is, String and byte[]) when used as input-only, and passed as YottaDB wrappers (GTMString and GTMByteArray, accordingly) when the direction is input-output or output-only; apply appropriate casting in the target Java method. The following table summarizes the type usage for YottaDB call-outs to Java:

+----------------------------+-----------------------------------------+--------------------------+
| Type in Java               | Type in CO Table                        | Use                      |
+============================+=========================================+==========================+
| GTMBoolean                 | gtm_jboolean_t                          | I, IO, O                 |
+----------------------------+-----------------------------------------+--------------------------+
| GTMInteger                 | gtm_jint_t                              | I, IO, O                 |
+----------------------------+-----------------------------------------+--------------------------+
| GTMLong                    | gtm_jlong_t                             | I, IO, O                 |
+----------------------------+-----------------------------------------+--------------------------+
| GTMFloat                   | gtm_jfloat_t                            | I, IO, O                 |
+----------------------------+-----------------------------------------+--------------------------+
| GTMDouble                  | gtm_jdouble_t                           | I, IO, O                 |
+----------------------------+-----------------------------------------+--------------------------+
| GTMString                  | gtm_jstring_t                           | IO, O                    |
+----------------------------+-----------------------------------------+--------------------------+
| GTMByteArray               | gtm_jbyte_array_t                       | IO, O                    |
+----------------------------+-----------------------------------------+--------------------------+
| String                     | gtm_jstring_t                           | I                        |
+----------------------------+-----------------------------------------+--------------------------+
| byte[]                     | gtm_jbyte_array_t                       | I                        |
+----------------------------+-----------------------------------------+--------------------------+

The call-out interface limits the total number of arguments to 29.

**Return Types**

Analogous to call-outs to C, the only allowed return types from Java are void (no value returned), ydb_status_t (int is returned), and gtm_jlong_t (long is returned). Returning a non-zero value with gtm_status_t return type results in an error.

**String Conversion**

The conversion between UTF-8 (used in M) and UTF-16 (used in Java) encodings applies the same way to call-outs with appropriate ordering (opposite from call-in).

**Exceptions**

Whenever the call out encounters an unhandled error condition - whether in the invocation processing or the Java program execution - the control returns to YottaDB, which raises an error. It is the application's responsibility to handle the error.

**Examples**

Consider the following example. The call-out table contains two entries:

.. parsed-literal::
   /usr/local/lib/yottadb/r122/plugin/libgtmm2j.so  
   f1:void gtm_xcj(I:gtm_jint_t,I:gtm_jlong_t,I:gtm_jdouble_t,I:gtm_jstring_t,I:gtm_jbyte_array_t) 
   f2:gtm_jlong_t gtm_xcj(IO:gtm_jboolean_t,IO:gtm_jfloat_t,IO:gtm_jstring_t,IO:gtm_jbyte_array_t) 

The first entry defines the 'f1' label, and the second entry—the 'f2' label, and "assigns" them to the package whose name is encoded in the GTMXC_<package_name> environment variable. In this example we assume it to be 'test'. The first function does not return a value and expects five arguments whose values would resolve to int, long, double, String, and byte[], respectively. The second function returns a long value and expects four arguments that would resolve to boolean, float, String, and byte[], respectively.

The Java class (which we assume to be com.fis.test.CO) contains the following:

.. parsed-literal::
   package com.fis.test;  
  
   import com.fis.gtm.ji.GTMBoolean;  
   import com.fis.gtm.ji.GTMByteArray;  
   import com.fis.gtm.ji.GTMCI;  
   import com.fis.gtm.ji.GTMDouble;  
   import com.fis.gtm.ji.GTMFloat;  
   import com.fis.gtm.ji.GTMInteger;  
   import com.fis.gtm.ji.GTMLong;  
   import com.fis.gtm.ji.GTMString;  
  
   public class CO {  
     public static void co1(Object[] args) {  
       GTMInteger gtmInteger = (GTMInteger)args[0];  
       GTMLong gtmLong = (GTMLong)args[1];  
       GTMDouble gtmDouble = (GTMDouble)args[2];  
       String javaString = (String)args[3];  
       byte[] javaByteArray = (byte[])args[4];  
  
       System.out.println(  
         "In co1():\n" +  
         "gtmInteger: " + gtmInteger + "\n" +  
         "gtmLong: " + gtmLong + "\n" +  
         "gtmDouble: " + gtmDouble + "\n" +  
         "javaString: " + javaString + "\n" +  
         "javaByteArray: " + new String(javaByteArray) + "\n" +  
         "----------------------");  
  
       gtmInteger.value = 3;  
       gtmLong.value = 141;  
       gtmDouble.value = 5.926;  
       javaString = "5358979";  
       javaByteArray[0] = (byte)51;  
     }    
  
     public static long co2(Object[] args) {  
       GTMBoolean gtmBoolean = (GTMBoolean)args[0];  
       GTMFloat gtmFloat = (GTMFloat)args[1];  
       GTMString gtmString = (GTMString)args[2];  
       GTMByteArray gtmByteArray = (GTMByteArray)args[3];  
  
       System.out.println(  
         "In xcallIO():\n" +  
         "gtmBoolean: " + gtmBoolean + "\n" +  
         "gtmFloat: " + gtmFloat + "\n" +  
         "gtmString: " + gtmString + "\n" +  
         "gtmByteArray: " + gtmByteArray + "\n" +  
         "----------------------");  
  
       gtmBoolean.value = true;  
       gtmFloat.value = 3.141f;  
       gtmString.value = "592653";  
       gtmByteArray.value = new byte[]{53, 56, 57};  
  
       return 321;  
     }  
   }

Finally, the M routine (which we assume to be 'rtns') looks like:

.. parsed-literal::
   co   
     set b=0,i=123,l=456,f=789,d=1011,s="1213",ba="1415"   
     set class="com/fis/test/CO"   
     write "Before f1 and f2:",!   
     write "b: "_b,!,"i: "_i,!,"l: "_l,!,"f: "_f,!,"d: "_d,!,"s: "_s,!,"ba: "_ba,!   
     write "----------------------",!   
     do &test.f1(class,"co1",i,l,d,s,ba)   
     hang 1   
     write "After f1 but before f2:",!   
     write "b: "_b,!,"i: "_i,!,"l: "_l,!,"f: "_f,!,"d: "_d,!,"s: "_s,!,"ba: "_ba,!   
     write "----------------------",!   
     set ret=$&test.f2(class,"co2",.b,.f,.s,.ba)   
     hang 1   
     write "After f1 and f2:",!   
     write "b: "_b,!,"i: "_i,!,"l: "_l,!,"f: "_f,!,"d: "_d,!,"s: "_s,!,"ba: "_ba,!   
     quit

If correctly configured, the execution of the above routine should yield this output:

.. parsed-literal::
   Before f1 and f2:   
   b: 0   
   i: 123   
   l: 456   
   f: 789   
   d: 1011   
   s: 1213   
   ba: 1415   
   ----------------------   
   In co1():   
   gtmInteger: 123   
   gtmLong: 456   
   gtmDouble: 1011.0   
   javaString: 1213   
   javaByteArray: 1415   
   ----------------------   
   After f1 but before f2:   
   b: 0   
   i: 123   
   l: 456   
   f: 789   
   d: 1011   
   s: 1213   
   ba: 1415   
   ----------------------   
   In xcallIO():   
   gtmBoolean: false   
   gtmFloat: 789.0   
   gtmString: 1213   
   gtmByteArray: 1415   
   ----------------------   
   After f1 and f2:   
   b: 1   
   i: 123   
   l: 456   
   f: 3.141   
   d: 1011   
   s: 592653   
   ba: 589

Similarly to the call-ins example, notice that while we attempt to modify the arguments inside the 'f1' function, they retain their original values after the &test.f1(class,"co1",...) call. The values do change, though, in 'f2', as seen after the $&test.f2(class,"co2",...) call. It is also important that the string and byte-array arguments passed from M in the first function are cast to String and byte[], whereas the second function casts them to GTMString and GTMByteArray, accordingly.

++++++++++++++++++++++++++
Additional Considerations
++++++++++++++++++++++++++

**Performance**

In addition to the tasks that JVM performs automatically on behalf of the user, YDBJava introduces overheads associated with argument processing, concurrency control, job scheduling, and resource allocation for classes and methods, and field bindings. In case of call-outs, the first call to Java starts the JVM, which may also cause a corresponding delay. For performance, YottaDB recommends making most Java invocations in the scope of one process lifetime, and to do as much work as possible in the context of one invocation.

It is also important to carefully choose the arguments on which both M and Java operate. Unnecessarily resorting to complex types and types with higher capacity adversely affects performance. This is especially true about byte arrays and strings, which undergo special allocation and conversion procedures.

**Numeric Conversions**

YottaDB has only two data types - canonical numbers and strings. A string call-in argument cannot exceed 1 MiB. If a numeric argument exceeds 18 significant digits (YottaDB internal limit for canonical numbers), YottaDB retains the most significant 18 digits before returning to Java. For performance reasons, YDBJava does not check for values of numeric arguments that fall outside the limits of the primitive Java type. It is the application's responsibility to enforce the following limits for numeric arguments for correct computation:

+------------------------+----------------------------------------------------------+---------------------------------------------------------+
| YDBJava Types          | YottaDB -> Java                                          | Java -> YottaDB                                         |
+                        +------------------------+---------------------------------+-----------------------------+---------------------------+
|                        | Precision              | Range - [Max, Min]              | Precision                   | Range - [Max, Min]        |
+========================+========================+=================================+=============================+===========================+
| GTMString              | NA                     | ["", 1MiB]                      | NA                          | ["", 1MiB]                |
+------------------------+------------------------+---------------------------------+-----------------------------+---------------------------+
| GTMInteger             | Full                   | [-2^31+1, 2^31-1]               | Full                        | [-2^31, 2^31-1]           |
+------------------------+------------------------+---------------------------------+-----------------------------+---------------------------+
| GTMLong                | 18 digits              | [-2^63+1, 2^63-1]               | 18 digits                   | [-2^63, 2^63-1]           |
+------------------------+------------------------+---------------------------------+-----------------------------+---------------------------+
| GTMFloat               | 6-9 digits             | [1E-43, 3.4028235E38]           | 6 digits                    | [1E-43, 3.4028235E38]     |
+------------------------+------------------------+---------------------------------+-----------------------------+---------------------------+
| GTMDouble              | 15-17 digits           | [1E-43, 1E47]                   | 15 digits                   | [1E-43, 1E47]             |
+------------------------+------------------------+---------------------------------+-----------------------------+---------------------------+
| **Precision** indicates the number of decimal digits retained when passing arguments within the corresponding numeric range.                |
+---------------------------------------------------------------------------------------------------------------------------------------------+
| For floating-point types (GTMFloat and GTMDouble), Range denotes absolute values.                                                           |
+---------------------------------------------------------------------------------------------------------------------------------------------+

Of the numeric types, it is generally safe to pass GTMInteger, GTMLong, and GTMFloat arguments from Java to M as they do not exceed YottaDB's numeric range; GTMDouble and BigDecimal, however, may cause numeric overflow if you use absolute values that are too big. On the M side, to avoid overflow issues, be sure not to assign values that the corresponding Java types cannot support; for instance, do not assign a value exceeding (2^32 - 1) to an argument which is defined as gtm_jint_t in the mapping table and would be interpreted as GTMInteger on the Java side.
