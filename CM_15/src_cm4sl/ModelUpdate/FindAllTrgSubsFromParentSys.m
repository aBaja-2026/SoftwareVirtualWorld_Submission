    function [subs] = FindAllTrgSubsFromParentSys (ParentSystem, Block, PutKind, NoInOutputs)
% Search for all systems that contain 'pattern' and are part of the subsystem 'subsystem'
% Returns an array of all found systems that contain the specified number of Inports/Outports
% 'ParentSystem' = 'NameOfParentSystem' (example: 'PowerTrain')
% 'Block' = 'NameOfBlock'               (example: 'Demux')
% 'PutKind' = 'Inputs' | 'Outputs'.     (example: 'Inputs')
% 'NoInOuputs' = 'NumberOfInOrOutputs'  (example: '42')

SetGlobal;

subs = [];

SubSystems = find_system(trg_mdl);

for i = 1:length(SubSystems)
    % Full block path + name (example: MyModel/Subsystem1/Demux)
    NameOfSubSystem = SubSystems(i);
    delim = strfind(NameOfSubSystem, '/');
    if isempty(delim{1}) == 1
        continue
    end
    NameOfSubSystemWithoutModelName = eraseBetween(NameOfSubSystem, 1, delim{1}(1));

    % Check if 'Block' is part of parent system
    rv = strfind(NameOfSubSystemWithoutModelName, ParentSystem, 'ForceCellOutput', true);
    if isempty(rv{1}) == 1
        continue
    end

    % Check 'Block' name
    rv = strfind(NameOfSubSystem, Block, 'ForceCellOutput', true);
    if isempty(rv{1}) == 1
     continue
    end

    % Check number of in or outputs of the 'Block'
    InOutputs = get_param(NameOfSubSystem, PutKind);
    if strcmp(InOutputs{1}, NoInOutputs) == 0
        continue
    end

    block_name = get_param(NameOfSubSystem, 'Name');
    parent_name = get_param(NameOfSubSystem, 'Parent');
    subs(end+1).blck   = block_name{1};
    subs(end).trgSys   = parent_name{1};
end
