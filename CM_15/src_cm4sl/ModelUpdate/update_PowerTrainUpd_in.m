opts = [];

sfunparam    = 'PowerTrainUpd';
ModSys       = 'BusCreator1';
ModifiedPort = 2; % PowerTrain
PortKind     = 'Inport';

subs_src = FindSrcSubsFromSFun(sfunparam, ModSys, ModifiedPort, PortKind);
subs_trg = FindAllTrgSubsFromParentSys('PowerTrain', 'BusCreator', 'Inputs', '42');

for i = 1:length(subs_trg)
    subs = [];
    subs.blck_src = subs_src.blck_src;
    subs.srcSys = subs_src.srcSys;
    subs.blck = subs_trg(i).blck;
    subs.trgSys = subs_trg(i).trgSys;

    opts.OldPortNumsIn  = [1, -1, 2:42];
    opts.OldPortNumsOut = [1];
    % opts.FontSizeLabel  = 2;
    opts.AddTerms       = 0;

    ReplaceAndReconnect(subs, opts);

    % Add constant block to model
    dest = strcat(subs.trgSys, '/Const');
    add_block('simulink/Sources/Constant', dest);
    % Connect new constant block to Bus Creator Input Port 2
    destName = strcat(subs.blck, '/2');
    add_line(subs.trgSys, 'Const/1', destName);
end

searchstring = "Bus" + newline + "Creator";
subs_trg = FindAllTrgSubsFromParentSys('PowerTrain', searchstring, 'Inputs', '42');

for i = 1:length(subs_trg)
    subs = [];
    subs.blck_src = subs_src.blck_src;
    subs.srcSys = subs_src.srcSys;
    subs.blck = subs_trg(i).blck;
    subs.trgSys = subs_trg(i).trgSys;

    opts.OldPortNumsIn  = [1, -1, 2:42];
    opts.OldPortNumsOut = [1];
    % opts.FontSizeLabel  = 2;
    opts.AddTerms       = 0;

    ReplaceAndReconnect(subs, opts);

    % Add constant block to model
    dest = strcat(subs.trgSys, '/Const1');
    add_block('simulink/Sources/Constant', dest);
    % Connect new constant block to Bus Creator Input Port 2
    destName = strcat(subs.blck, '/2');
    add_line(subs.trgSys, 'Const1/1', destName);
end

clear opts subs;
