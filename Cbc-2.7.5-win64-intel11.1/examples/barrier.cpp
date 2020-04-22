// $Id$
// Copyright (C) 2006, International Business Machines
// Corporation and others.  All Rights Reserved.
// This code is licensed under the terms of the Eclipse Public License (EPL).

#if defined(_MSC_VER)
// Turn off compiler warning about long names
#  pragma warning(disable:4786)
#endif

#include <cassert>
#include <iomanip>


#include "OsiClpSolverInterface.hpp"
#include  "CoinTime.hpp"

//#############################################################################


/************************************************************************

This main program reads in a model from an mps file.

It then tells the OsiClpSolver to use barrier for initialSolve

The cryptic code was generated by playing around with "clp" and using -cpp
option.

So 
clp input.mps -cpp 1 -barrier

created a user_driver.cpp from which the lines between ===== were taken

************************************************************************/

int main (int argc, const char *argv[])
{

  // Define your favorite OsiSolver
  
  OsiClpSolverInterface solver1;
  // Taken from a user_driver.cpp
  // =======================
  ClpSolve::SolveType method = ClpSolve::useBarrier;
  ClpSolve::PresolveType presolveType = ClpSolve::presolveOn;
  int numberPasses = 5;
#ifndef UFL_BARRIER
  int options[] = {0,0,0,0,0,0};
#else
  // we can use UFL code
  int options[] = {0,0,0,0,4,0};
#endif
  int extraInfo[] = {-1,-1,-1,-1,-1,-1};
  int independentOptions[] = {0,0,3};
  ClpSolve clpSolve(method,presolveType,numberPasses,
                    options,extraInfo,independentOptions);
  // =======================
  // now pass options in
  solver1.setSolveOptions(clpSolve);
  // Read in model using argv[1]
  // and assert that it is a clean model
  std::string mpsFileName;
#if defined(SAMPLEDIR)
  mpsFileName = SAMPLEDIR "/p0033.mps";
#else
  if (argc < 2) {
    fprintf(stderr, "Do not know where to find sample MPS files.\n");
    exit(1);
  }
#endif
  if (argc>=2) mpsFileName = argv[1];
  int numMpsReadErrors = solver1.readMps(mpsFileName.c_str(),"");
  assert(numMpsReadErrors==0);
  double time1 = CoinCpuTime();

  solver1.initialSolve();

  std::cout<<mpsFileName<<" took "<<CoinCpuTime()-time1<<" seconds, "
	   <<" with objective "
	   <<solver1.getObjValue()
	   <<std::endl;

  return 0;
}    
