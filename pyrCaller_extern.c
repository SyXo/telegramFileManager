#include <stdio.h>

size_t
splitFile(size_t startIndex, const char *filePath, const char *outFileName,
		size_t mulChunkSize, size_t memChunkSize)
{
	// This function takes as arguments the size of the file buf that will
	// be in memory at a time and multiplies it by mulChunkSize to get
	// the whole chunk size.
	// This is in order to be more efficient because division is less
	// efficient than multiplication.
	//
	// Returns after every finished chunk

	FILE *in_fil, *out_fil;
	char buf[memChunkSize];
	size_t act_read;

	in_fil = fopen(filePath, "r");
	out_fil = fopen(outFileName, "w");

	fseek(in_fil, startIndex, SEEK_SET); // go to index
	for (size_t i = 0; i < mulChunkSize; ++i) {
		act_read = fread(buf, 1, memChunkSize, in_fil);
		fwrite(buf, 1, act_read, out_fil);

		if (act_read < memChunkSize) { // reached end of file
			fclose(in_fil);
			fclose(out_fil);
			return 0;
		}
	}
	act_read = fread(buf, 1, 1, in_fil);
	fclose(in_fil);
	fclose(out_fil);

	if (act_read) { // file continues
		return mulChunkSize*memChunkSize+startIndex;
	}
	return 0; // else file ended
}

char
concatFiles(const char *filePath, const char *outFileName, size_t memChunkSize)
{
	// Opens filePath and appends the contents of it to outFileName
	//
	// returns 0 if successful

	FILE *in_fil, *out_fil;
	char buf[memChunkSize]; // stores data from read file
	size_t act_read;

	in_fil = fopen(filePath, "r");
	if (!in_fil)
		return 1;

	out_fil = fopen(outFileName, "a");

	do {
		act_read = fread(buf, 1, memChunkSize, in_fil);
		if (!act_read)
			break;

		fwrite(buf, 1, act_read, out_fil);

	} while (act_read == memChunkSize); // read file not finished

	fclose(in_fil);
	fclose(out_fil);
	return 0;
}
