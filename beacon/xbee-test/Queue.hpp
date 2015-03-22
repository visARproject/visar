#include <stdlib.h>

template <class T, size_t size>
class Queue {
	T backend[size];

	// read will point to the next item to be dequeued, write will point to first empty spot
	// -- three cases:
	// -- -- 1. read pointer less than write pointer    -- elements in queue
	// -- -- 2. read pointer greater than write pointer -- wrap-around; there remains room unless read == write
	// -- -- 3. read pointer equal to write pointer     -- empty if no wrap-around, full if wrap-around
	int read, write;

	// necessary to calculate the size, unless we use a std::array or std::vector,
	// but the first requires a known size at compile-time, and the second is overkill
	//size_t size;

	// I think there's a way to do without this if we let the read/write pointers grow
	// past the max size, but we'd have to perform modulo operations constantly for each enqueue/dequeue, which can be expensive
	// (what if we made a lookup table to precompute the possible remainders? then we'd be using another array...)
	bool wrapped;

public:
	Queue() : read(0), write(0), wrapped(false) {

	};

	bool isEmpty(){
		if(read == write && !wrapped){
			return true;
		} else {
			return false;
		}
	}

	bool isFull(){
		if(read == write && wrapped){
			return true;
		} else {
			return false;
		}
	}

	void enqueue(T in){
		if(this->isFull()){
			return; // don't try to write to a full queue!
		}

		backend[write] = in;
		if(write == size - 1){ // if we exceed the size, wrap around to zero
			write = 0;
			wrapped = true;
		} else {
			write++;
		}
	}

	T dequeue(){
		if(this->isEmpty()){
			return backend[read]; // not sure how to handle this,
								  // so let's just return the last element
								  // and not mess up the read/write pointers
		}

		int tmp = read;
		if(read == size - 1){ // if we exceed the size, reset to zero...
			read = 0;
			wrapped = false; // ... but now read is less than write and we are un-wrapped
		} else {
			read++;
		}
		return backend[tmp];
	}

	size_t current_size(){
		if(wrapped){
			return size+write-read;
		} else {
			return write-read;
		}
	}

};

