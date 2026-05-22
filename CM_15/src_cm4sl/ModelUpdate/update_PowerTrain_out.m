opts = [];
SetGlobal;

sfunparam    = 'PowerTrain';
ModSys       = 'Demux1';
ModifiedPort = 2; % PowerTrain
PortKind     = 'Outport';

subs_src = FindSrcSubsFromSFun(sfunparam, ModSys, ModifiedPort, PortKind);
subs_trg = FindAllTrgSubsFromParentSys('PowerTrain', 'Demux', 'Outputs', '42');

for i=1:length(subs_trg)
    subs = [];
    subs.blck_src = subs_src.blck_src;
    subs.srcSys = subs_src.srcSys;
    subs.blck = subs_trg(i).blck;
    subs.trgSys = subs_trg(i).trgSys;

    opts.OldPortNumsIn  = [1];
    opts.OldPortNumsOut = [1, -1, 2:42];
    % opts.FontSizeLabel  = 2;
    opts.AddTerms       = 1;

    ReplaceAndReconnect(subs, opts);
end

clear opts subs;
