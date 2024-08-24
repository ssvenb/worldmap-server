#include <Python.h>
#include <wiringPi.h>
#include <stdio.h>
#include <time.h>

#define SAFE 27
#define CLOCK 28
#define DATA 29

struct timespec req, rem;

void activateAllPins() {
    wiringPiSetup();
    pinMode(SAFE, OUTPUT);
    pinMode(CLOCK, OUTPUT);
    pinMode(DATA, OUTPUT);
}

void deactivateAllPins() {
    pinMode(SAFE, INPUT);
    pinMode(CLOCK, INPUT);
    pinMode(DATA, INPUT);
}

void triggerPin(int pin) {
    req.tv_sec = 0;
    req.tv_nsec = 1;
    nanosleep(&req, &rem);
    digitalWrite(pin, HIGH);
    nanosleep(&req, &rem);
    digitalWrite(pin, LOW);
}

void save() {
    triggerPin(SAFE);
}

void clock_tick() {
    triggerPin(CLOCK);
}

void writeAll(int leds[], int size) {
    for (int reg = 0; reg < size; reg++) {
        for (int i = 0; i < 16; i++) {
            digitalWrite(DATA, (leds[reg] >> i) & 1);
            clock_tick();
        }
    }
    save();
}

static PyObject* _activate(PyObject* self) {
    activateAllPins();
    Py_RETURN_NONE;
}

static PyObject* _light(PyObject* self, PyObject* args) {
    PyObject* list_obj;
    if (!PyArg_ParseTuple(args, "O", &list_obj)) {
        PyErr_SetString(PyExc_TypeError, "No input provided");
        return NULL;
    }

    if (!PyList_Check(list_obj)) {
        PyErr_SetString(PyExc_TypeError, "Expected a list of integers");
        return NULL;
    }

    int list_size = 9;
    if (PyList_Size(list_obj) != list_size) {
        PyErr_SetString(PyExc_TypeError, "The size of the list should be 9");
        return NULL;
    }

    int bitmap[list_size];
    for (Py_ssize_t i = 0; i < list_size; i++) {
        PyObject* item = PyList_GetItem(list_obj, i);
        if (!PyLong_Check(item)) {
            PyErr_SetString(PyExc_TypeError, "List elements must be integers");
            return NULL;
        }
        bitmap[i] = (int)PyLong_AsLong(item);
    }

    writeAll(bitmap, list_size);

    Py_RETURN_NONE;
}

static struct PyMethodDef methods[] = {
    {"activate", (PyCFunction)_activate, METH_NOARGS},
    {"light", (PyCFunction)_light, METH_VARARGS},
    {NULL, NULL}
};

static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "ledmodule",
    "This module provides functions to light up leds on a worldmap",
    -1,
    methods
};

PyMODINIT_FUNC PyInit_ledmodule(void) {
    return PyModule_Create(&module);
}