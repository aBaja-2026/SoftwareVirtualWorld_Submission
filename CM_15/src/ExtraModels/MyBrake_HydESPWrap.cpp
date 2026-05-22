/*
 *****************************************************************************
 *  CarMaker - Version 15.0
 *  Virtual Test Driving Tool
 *
 *  Copyright ©1998-2025 IPG Automotive GmbH. All rights reserved.
 *  www.ipg-automotive.com
 *****************************************************************************
 *
 * A Wrapper around an existing, already registered brake model,
 * implementing alternative park brake handling.
 *
 * Add the declaration of the register function to one of your header files,
 * for example to User.h and call it in User_Register()
 *
 *	Brake_Register_MyModelHydESPWrap();
 *
 *****************************************************************************
 */

#include <Global.h>

#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "CarMaker.h"
#include "ModelManager.h"
#include "Car/Vehicle_Car.h"
#include "MyModels.h"

#define NWHEEL 4

static char const ThisModelClass[] = "Brake.System";
static char const ThisModelKind[]  = "HydESPWrap";

struct tMyModel {
    /* Additional signals, outputs, ... */
    // double Trq[NWHEEL]; /* park brake torque */

    /* Parameters */
    double PBTrq_max[NWHEEL]; /* max. park brake torque for VC.BrakePark==1 */

    /* wrapped model: functions New/Calc/Delete/... */
    tModelClassDescr Wrapped;

    void *Wrapped_param; /* wrapped model: parameter handle */
};

static void
MyModel_DeclQuants_dyn(struct tMyModel *mp, char const *Ident, int park)
{
    static struct tMyModel MyModel_Dummy = {{0}};
    if (park) {
        mp = &MyModel_Dummy;
    }

    /* Define here dict entries for dynamically allocated variables. */

    /* Call wrapped hydraulic brake model quantities */
    if (mp->Wrapped.DeclQuants != NULL) {
        mp->Wrapped.DeclQuants(mp->Wrapped_param, Ident);
    }

    /* Quantities of the wrapper model */
    // DDefDouble(NULL, "Brake.<xyz>.Trq_RL", "bar", &mp->Trq[2], DVA_None);
    // DDefDouble(NULL, "Brake.<xyz>.Trq_RL", "bar", &mp->Trq[3], DVA_None);
}

static void
MyModel_DeclQuants(void *MP, char const *Ident)
{
    struct tMyModel *mp = (struct tMyModel *) MP;

    if (mp == NULL) {
        /* Define here dict entries for non-dynamically allocated (static) variables. */

    } else {
        MyModel_DeclQuants_dyn(mp, Ident, 0);
    }
}

static void *
MyModel_New(struct tInfos *Inf, void *pCfgIF, char const *KindKey, char const *IdKey)
{
    struct tMyModel       *mp    = NULL;
    struct tHydBrakeCfgIF *CfgIF = (struct tHydBrakeCfgIF *) pCfgIF;
    tModelClassDescr      *md;
    char const            *key;
    char                   MsgPre[64];
    double                 dvec[NWHEEL];
    int                    i;

    sprintf(MsgPre, "%s %s", ThisModelClass, ThisModelKind);

    mp = (struct tMyModel *) calloc(1, sizeof(struct tMyModel));

    /* Get interface functions of wrapped model. */
    if ((md = Model_Lookup(ModelClass_HydBrakeSystem, "HydESP")) == NULL) {
        LogErrF(EC_Init, "%s: Missing brake model '%s'", MsgPre, "HydESP");
        goto ErrorReturn;
    }
    mp->Wrapped = *md;

    /* Initialize wrapped model. */
    if (mp->Wrapped.New != NULL) {
        mp->Wrapped_param = mp->Wrapped.New(Inf, CfgIF, KindKey, IdKey);
        if (mp->Wrapped_param == NULL) {
            goto ErrorReturn;
        }
    }

    /* Get model parameters. */
    key = "Park.BrakePark2Trq";
    iGetTable(Inf, key, dvec, NWHEEL, 1, &i);
    if (i != NWHEEL) {
        LogErrF(EC_Init, "%s: Unsupported argument for '%s'", MsgPre, key);
        goto ErrorReturn;
    }

    for (i = 0; i < NWHEEL; i++) {
        mp->PBTrq_max[i] = dvec[i];
    }

    return mp;

ErrorReturn:
    free(mp);
    return NULL;
}

static int
MyModel_Calc(void *MP, void *pIF, void *pIF2, double dt)
{
    struct tMyModel    *mp = (struct tMyModel *) MP;
    struct tHydBrakeIF *IF = (struct tHydBrakeIF *) pIF;
    int                 i;

    /* Call wrapped hydraulic brake model. */
    if (mp->Wrapped.Calc(mp->Wrapped_param, IF, NULL, dt) < 0) {
        return -1;
    }

    for (i = 0; i < NWHEEL; i++) {
        IF->Trq_PB[i] = mp->PBTrq_max[i] * VehicleControl.BrakePark;
    }

    return 0;
}

static void
MyModel_Delete(void *MP, char const *Ident)
{
    struct tMyModel *mp = (struct tMyModel *) MP;

    /* Park the dict entries for dynamically allocated variables before deleting */
    MyModel_DeclQuants_dyn(mp, (char *) Ident, 1);

    if (mp->Wrapped_param != NULL && mp->Wrapped.Delete != NULL) {
        mp->Wrapped.Delete(mp->Wrapped_param, Ident);
    }

    free(mp);
}

int
Brake_Register_MyModelHydESPWrap(void)
{
    tModelClassDescr  mp;
    tModelClassDescr *md;
    char              MsgPre[64];

    sprintf(MsgPre, "%s %s", ThisModelClass, ThisModelKind);
    if ((md = Model_Lookup(ModelClass_HydBrakeSystem, "HydESP")) == NULL) {
        LogErrF(EC_Init, "%s: Missing brake model '%s'", MsgPre, "HydESP");
        return -1;
    }

    memset(&mp, 0, sizeof(mp));
    mp.VersionId  = md->VersionId;
    mp.New        = MyModel_New;
    mp.Calc       = MyModel_Calc;
    mp.Delete     = MyModel_Delete;
    mp.DeclQuants = MyModel_DeclQuants;
    /* Should only be used if the model doesn't read params from extra files */
    mp.ParamsChanged = ParamsChanged_IgnoreCheck;

    return Model_Register(ModelClass_HydBrakeSystem, ThisModelKind, &mp);
}
