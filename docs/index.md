# structure #

Storage need for one float value:

```
id + value 	+ time_id + variable_id
64 + 64  	+ 64 	  + 11
```

## valid data types ##

	`BOOL`						1	1/16 WORD		
	`UINT8` `BYTE`				8	1/2 WORD
	`INT8`						8	1/2 WORD
	`UNT16` `WORD`				16	1 WORD
	`INT16`						16	1 WORD
	`UINT32` `DWORD`			32	2 WORD
	`INT32`						32	2 WORD
	`FLOAT` `FLOAT32` `SINGLE` 	32	2 WORD
	`FLOAT64` `DOUBLE`			64	4 WORD