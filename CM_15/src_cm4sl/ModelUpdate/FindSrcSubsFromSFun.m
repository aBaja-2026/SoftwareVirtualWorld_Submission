    function [subs] = FindSrcSubsFromSFun (sfunparam, ModSys, ModifiedPort, PortKind)
% Search for systems attached to S-Function 'sfunparam' at Port 'ModifiedPort'.
% ONLY returns systems from src mdl file
% 'ModSys' is the block name in the src system.
% 'PortKind' = Inport | Outport.
% 'ModifiedPort' = -1 stores the S-Fun itself in 'subs' for later substitution.
subs = [];

SFun_matches = FindSFun(sfunparam);

srcBlck   = SFun_matches.srcBlck;
srcSys    = SFun_matches.srcSys;
BlockType = SFun_matches.BlockType;

for (j=1:numel(srcBlck))
    % get all ports on trg block
    ports.old = get_param(srcBlck{j},'PortHandles');

    % get all lines attached to trg block
    h     = get_param(srcBlck{j},'LineHandles');
    line = SaveConnections(h);

    if (strcmp(PortKind, 'Inport'))
        for (i=1:numel(line.in))
            if (line.in(i).DstPortHandle == ports.old.Inport(ModifiedPort))
                subs(end+1).blck_src = ModSys; % name from generic_truck in TM12
                subs(end).srcSys   = srcSys{1};
            end
        end
    elseif (strcmp(PortKind, 'Outport'))
        for (i=1:numel(line.out))
            if (line.out(i).SrcPortHandle==ports.old.Outport(ModifiedPort))
                subs(end+1).blck_src = ModSys; % name from generic_truck in TM12
                subs(end).srcSys   = srcSys{1};
            end
        end
    else
        % Bug/missuse
        warning("No valid PortKind (Inport | Outport). Got ''%s'' instead.", PortKind);
    end
end
