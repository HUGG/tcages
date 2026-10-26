//---------------------------------------------------------------------------

#pragma hdrstop

#include "RDAAM.h"
#include <string>

//---------------------------------------------------------------------------

#if defined(_WIN32) || defined(_WIN64)
#define EXPORT extern "C" __declspec(dllexport)
#else
#define EXPORT extern "C"
#endif

EXPORT TTPath* make_path() {
  return new TTPath();
}

EXPORT void path_push(TTPath* path, double time, double temperature) {
  path->push_back({time, temperature});
}

EXPORT void del_path(TTPath* path) {
  if (path == nullptr) {
    return;
  }
  delete path;
}

EXPORT void run_RDAAM_He(
    TTPath* path, double ap_rad, double ap_U, double ap_Th, double* ap_age, 
    double* ap_corrAge, double total_He, double zr_rad, double zr_U, double zr_Th,
    double* zr_age, double* zr_corrAge, int* ap_success, int* zr_success) {
    // Run this first to set up the model.  Run again if you change one of the parameters
    RDAAM_Init(HE_PREC_BEST, ap_rad, ap_U, ap_Th, 0.0); // precision, radius, U, Th, Sm

    // After RDAAM_Init is run, run this as many times as you want for each path to model
    // Set final parameter (optimize) to true for geological histories, false for degassing
    int ap_succ = RDAAM_Calculate(path, *ap_age, *ap_corrAge, total_He, false);
    ap_success[0] = ap_succ;

    // For zircon, just change the first letter
    ZRDAAM_Init(HE_PREC_BEST, zr_rad, zr_U, zr_Th, 0.0); // precision, radius, U, Th, Sm
    zr_success[0] = RDAAM_Calculate(path, *zr_age, *zr_corrAge, total_He, false);

    // Once you are done with this calculation, run this to clean up.
    RDAAM_FreeCalcArrays();
}
