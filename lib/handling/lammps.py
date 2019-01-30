#!/usr/bin/python
#    By Hernan Chavez Thielemann
__author__ = 'Hernan Chavez Thielemann <hchavezthiele at gmail dot com>'

from lib.misc.file import write_file
from lib.misc.warn import print_dec_g, pop_wrg_1, pop_err_1

from sys import exit

                    

def extract_lammps_data(_data_file_,_ck_buttons_, _forcefield_):
    ''' already implemented in  topology analizer
            MIXER
    '''

def write_lammps_data( _topodata_, df_name, _config_):
    ''' Write a lammps data file'''
    print_dec_g ('Writing Lammps data file...')
    ####---------------  Unpacking data  ----------------####
    atomstyle, _, _autoload_ = _config_
    atsty = [ 'atomic', 'angle', 'full', 'charge', 'bond', 'molecular']
    style_str = '####-------  ATOM STYLE < {} >  --------####'
    _flag_ = False
    _content_=''
    if atomstyle in atsty:
        nam = ''.join([ chr( ord(l) - 32) for l in atomstyle])
        print_dec_g(style_str.format(nam))
        
        if _autoload_:
            print '\n'+'='*10+' Still in BETA here '+'='*10+'\n'
            _content_, _flag_ = write_lammps_data_auto( _topodata_,
                                                        df_name,
                                                        _config_
                                                      )
            
        else:
            _content_, _flag_ = write_lammps_data_all( _topodata_,
                                                       df_name,
                                                       _config_
                                                     )
        errmsg = 'Error writing lammps data file'
        if _flag_:
            write_file( df_name, _content_)
            print_dec_g ('Successful writing!!')
        elif _autoload_:
            pop_err_1(errmsg + '\nAutoload failed!')
        else:
            pop_err_1(errmsg)
    else: #if atomstyle == 'Angle':
        print '\n\nExit'
        exit(('Error 037!!  -  Atom style {} '
              +'not implemented yet').format(atomstyle))
    
    return _flag_

def write_lammps_data_all( _topodata_, data_name, _config_):
    
    ''' Write a lammps data file'''
    _flag_ = False
    ####---------------  Unpacking data  ----------------####
    _numbers_ = _topodata_['numbers']
    
    n_atoms, n_bonds, n_angles, n_dihedrals, _ = _numbers_['total']
    n_atomtypes, n_bondtypes, n_angletypes = _numbers_['type'][:3]
    n_dihedraltypes, n_impropertypes = _numbers_['type'][3:]
    
    _box_= _topodata_['box']
    _mol_, _mtype_, _atype_, _xyz_, _ = _topodata_['atomsdata'] 
    
    atomstyle, _solvated_f_, _ = _config_ 
    
    _asty_d_ ={ 'atomic':1, 'charge':1, 'bond':2, 'angle':3,
                'full':4, 'molecular':4}
    ####--------------- TITLE ----------------####
    _text_ = '#Lammps data file. Geometry for PEG. By GRO2LAM converter.\n\n'
    ####---------------     NUMBERS      ----------------####
    _aux_txt =[' {} atoms\n'.format(n_atoms)]
    _aux_txt.append(' {} bonds\n'.format( n_bonds))
    _aux_txt.append(' {} angles\n'.format( n_angles))
    _aux_txt.append(' {} dihedrals\n'.format( n_dihedrals))
    _text_+= ''.join(_aux_txt[:_asty_d_[atomstyle]])+'\n'
    ####----------------    TYPES       -----------------####
    _aux_txt =[' {} atom types\n'.format(n_atomtypes)]
    _aux_txt.append(' {} bond types\n'.format(n_bondtypes))
    _aux_txt.append(' {} angle types\n'.format(n_angletypes))
    _aux_txt.append(' {} dihedral types\n\n'.format(n_dihedraltypes))
    _text_+= ''.join(_aux_txt[:_asty_d_[atomstyle]])+'\n'
    ####----------------    BOX     -----------------####
    _text_ +=(' {:.4f} {:.4f} xlo xhi\n {:.4f} {:.4f} ylo yhi\n'
              +' {:.4f} {:.4f} zlo zhi\n').format(*_box_)
    #####------             MASSES              ------####
    _text_ +='\n Masses\n\n'
    atom_info = _topodata_['atomtypes']
    for i in range( n_atomtypes):
        _text_ +=' {} {} # {}\n'.format( i+1, atom_info[i][1], atom_info[i][0])
        
    #####------             Force field potentials               ------####
    
    #for na in range(len(known_atoms)):
        #if known_atoms[na][4] not in charge.keys():
        #   print known_atoms[na][4], known_atoms[na][6]
        #charge[known_atoms[na][4]]= float(known_atoms[na][6])
        #conv_dict[known_atoms[na][4].lstrip(' ')] = known_atoms[na][1]
    #_topodata_['S_translation'] = conv_dict
    
    
    aux_pot_txt, dicts, _flag_ = write_lammps_potentials( _topodata_,
                                                          atomstyle)
    _text_ += aux_pot_txt
    #a_dict={}
    #print dicts[0]
    #for key in conv_dict.keys(): # key - short
    #    
    #    a_dict[key]= dicts[0][conv_dict[key]]
    #print a_dict
    
    
    ####------ATOMS------####
    known_atoms = _topodata_['atoms']
    if _solvated_f_ == 1:
        charge = _topodata_['S_charge']
        conv_dict = _topodata_['S_translation'] # key s_tag : val l_tag
    
    
    _text_ +='\n Atoms #{}\n\n'.format( atomstyle)
    
    if atomstyle in ['charge','full']:
        atom_shape = ' {}'*3+' {:7.4f}'*4+' # {}\n'# idx mol atype charge x y z
    elif atomstyle in ['bond','angle','molecular']:
        atom_shape = ' {0} {1} {2} {4:7.4f} {5:7.4f} {6:7.4f} # {7}\n'
    elif atomstyle =='atomic':
        atom_shape = ' {0} {2} {4:7.4f} {5:7.4f} {6:7.4f} # {7}\n'
        
    base_atoms_n = len( known_atoms)
    for i in range( base_atoms_n):
        aty = known_atoms[i][1]
        _text_ += atom_shape.format( i+1, _mol_[i],
                                    dicts[0][ aty],
                                    float(known_atoms[ i][6]),
                                    float(_xyz_[i][0])*10,
                                    float(_xyz_[i][1])*10,
                                    float(_xyz_[i][2])*10,
                                    aty
                                   )
    solv_bonds = []
    solv_angles = []
    # asumption: all solvated structures are water??
    # 
    if _solvated_f_ == 1:
        solv_at_v = range(n_atoms )[ base_atoms_n:]
        for i in solv_at_v:
            aty = conv_dict[_atype_[i]]
            _text_ += atom_shape.format(i+1, _mol_[i], dicts[0][aty],
                                        charge[aty],
                                        float(_xyz_[i][0])*10,
                                        float(_xyz_[i][1])*10,
                                        float(_xyz_[i][2])*10,
                                        aty
                                       )
            if charge[aty] <0:
                # better way to do this is trough coords ---------  <WFS>
                # but anyway works perfectly
                aty2 = conv_dict[_atype_[i+1]]
                aty3 = conv_dict[_atype_[i+2]]
                solv_bonds.append([aty+'-'+aty2, i+1, i+2])
                solv_bonds.append([aty+'-'+aty3, i+1, i+3])
                solv_angles.append([aty2+'-'+aty+'-'+aty3, i+2, i+1, i+3])
    
    
    ####------BONDS------####
    if _asty_d_[atomstyle]>=2:
        known_bonds = _topodata_['bonds']
        base_bonds_n = len (known_bonds)
        _text_ +='\n Bonds\n\n'
        bond_shape = ' {}'*4+'\n'
        for i in range(base_bonds_n):
            
            at1 = int(known_bonds[i][0])
            at2 = int(known_bonds[i][1])
            
            _bond_ty_ = dicts[1][known_atoms[at1-1][1]+'-'
                                 +known_atoms[at2-1][1]]
            _text_ += bond_shape.format( i+1, _bond_ty_, at1, at2)
                        
        if _solvated_f_ == 1:
            # better way to do this is trough corrds ---------  <WFS>
            for i in range(n_bonds-base_bonds_n):
                _bond_ty_ = dicts[1][solv_bonds[i][0]]
                _text_ += bond_shape.format(i+1+base_bonds_n,_bond_ty_,
                                            solv_bonds[i][1],solv_bonds[i][2])
    
    
    ####------ANGLES------#########
    if _asty_d_[atomstyle]>=3:
        known_angles = _topodata_['angles']
        base_angles_n = len(known_angles)
        _text_ +='\n Angles\n\n'
        angle_shape = ' {}'*5+'\n'
        for i in range(base_angles_n):
            
            at1 = int(known_angles[i][0])
            at2 = int(known_angles[i][1])
            at3 = int(known_angles[i][2])
            
            angle_t = (known_atoms[at1-1][1]+'-'+ known_atoms[at2-1][1]
                       +'-'+known_atoms[at3-1][1])
            _angle_ty_ = dicts[2][angle_t]
            
            #print angle_t, _angle_ty_
            _text_ += angle_shape.format( i+1, _angle_ty_, at1, at2, at3)
            
        if _solvated_f_ == 1:
            
            for i in range(n_angles-base_angles_n):
                _angle_ty_ = dicts[2][solv_angles[i][0]]
                
                _text_ += angle_shape.format(i+1+base_angles_n, _angle_ty_,
                                             solv_angles[i][1],
                                             solv_angles[i][2],
                                             solv_angles[i][3]
                                            )
    
    
    ####------DIHEDRAL------####
    if _asty_d_[atomstyle]==4:
        known_dihedrals = _topodata_['dihedrals']
        base_dihedrals_n = len(known_dihedrals)
        _text_ +='\n Dihedrals\n\n'
        dihedral_shape = ' {}'*6+'\n'
        for i in range(base_dihedrals_n):
            
            at1 = int(known_dihedrals[i][0])
            at2 = int(known_dihedrals[i][1])
            at3 = int(known_dihedrals[i][2])
            at4 = int(known_dihedrals[i][3])
            
            _dihe_ty_ = dicts[3][known_atoms[at1-1][1]+'-'
                                 +known_atoms[at2-1][1]+'-'
                                 +known_atoms[at3-1][1]+'-'
                                 +known_atoms[at4-1][1]
                                ]
            _text_+= dihedral_shape.format( i+1, _dihe_ty_, at1, at2, at3, at4)
    
    
    return _text_, _flag_

def write_lammps_data_auto( _topodata_, data_name, _config_):
    ''' Write a lammps data file
        now with autoload,
        including impropers dihedrals (Aka Wop)
    '''
    
    _flag_ = False
    ####---------------  Unpacking data  ----------------####
    _numbers_ = _topodata_['numbers']
    n_atoms, n_bonds, n_angles, n_dihedrals, n_impropers = _numbers_['total']
    n_atomtypes, n_bondtypes, n_angletypes = _numbers_['type'][:3]
    n_dihedraltypes, n_impropertypes = _numbers_['type'][3:]
    _box_= _topodata_['box']
    _mol_, _mtype_g_, _atype_, _xyz_, _mtype_ = _topodata_['atomsdata'] 
    
    atomstyle, _sidemol_f_, _autoload_ = _config_ 
    
    if _sidemol_f_:
        sidemol = _topodata_['sidemol']
        
    _asty_d_ ={ 'atomic':1, 'charge':1, 'bond':2, 'angle':3,
                'full':4, 'molecular':4}
    
    #########################################################
    '''--------------      1st  Header      --------------'''
    #=======================================================#
    
    ####---------------     TITLE        ----------------####
    _text_ = '#Lammps data file. Geometry for PEG. By GRO2LAM converter.\n\n'
    ####---------------     NUMBERS      ----------------####
    _aux_txt = [' {} atoms\n'.format( n_atoms)]
    _aux_txt.append(' {} bonds\n'.format( n_bonds))
    _aux_txt.append(' {} angles\n'.format( n_angles))
    _aux_txt.append(' {} dihedrals\n'.format( n_dihedrals))
    _aux_txt.append(' {} impropers\n'.format( n_impropers))
    _text_ += ''.join( _aux_txt[:_asty_d_[atomstyle]])+'\n'
    
    ####----------------    TYPES       -----------------####
    _aux_txt = [ ' {} atom types\n'.format( n_atomtypes)]
    _aux_txt.append( ' {} bond types\n'.format( n_bondtypes))
    _aux_txt.append( ' {} angle types\n'.format( n_angletypes))
    _aux_txt.append( ' {} dihedral types\n\n'.format( n_dihedraltypes))
    _aux_txt.append( ' {} improper types\n\n'.format( n_impropertypes))
    _text_ += ''.join( _aux_txt[ : _asty_d_[ atomstyle]]) + '\n'
    
    ####----------------    BOX     -----------------####
    _text_ +=(' {:.4f} {:.4f} xlo xhi\n {:.4f} {:.4f} ylo yhi\n'
              +' {:.4f} {:.4f} zlo zhi\n').format(*_box_)
    
    #######################-------------------------###########################
    '''---------           2nd  Atom kind Properties             -----------'''
    #======================-------------------------==========================#
    
    #####------                       MASSES                         ------####
    _text_ +='\n Masses\n\n'
    atom_info = _topodata_['atomtypes']
    minr = 1 - int( _topodata_[ 'defaults'][0]) # 0 lj and -1 buck
    
    for i in range( n_atomtypes):
        _atom_mass_ = atom_info[i][ -5 + minr]
        _atom_type_ = atom_info[i][0]
        
        if not float( _atom_mass_) and _sidemol_f_: #meaning that is 0
            
            smols = sidemol['tag']
            #print 'here1', smols
            for ad in range( len(smols)):
                _smda_ = sidemol['data'][ad]['atoms']
                #print _smda_
                at_ = 0
                for at_ in range( len( _smda_)):
                    #print _smda_[at_], at_
                    if _smda_[at_][1] == _atom_type_ and len(_smda_[at_]) == 8:
                        _atom_mass_ = _smda_[at_][7]
                        print ( ('Mass for {} not found in atomtypes, taking' 
                                 + ' {} as substitute').format( _atom_type_, 
                                                                _atom_mass_)
                              )
                        break
                #if len(_smda_[at_]) == 8 and _atom_mass_ == _smda_[at_][7]:
                #    print at_
                #    break
        if not float( _atom_mass_):
            _atom_mass_ = '0.01008' # H_mass/100 as minimum seems reasonable
            pop_wrg_1( ('0.0 mass not supported! using {} instead for {} ' +
                        'atom type').format( _atom_mass_, _atom_type_) ) 
        
        _text_ +=' {} {} # {}\n'.format( i+1, _atom_mass_, _atom_type_)
        
    #======================-------------------------==========================#
    #####------                    Force field                       ------####
    
    aux_pot_txt, dicts, _flag_ = write_lammps_potentials( _topodata_,
                                                          atomstyle)
    _text_ += aux_pot_txt
    
    #########################################################
    '''-----------       3rd  Atom Coords     ------------'''
    #=======================================================#
    
    ####------                       ATOMS                           ------####
    known_atoms = _topodata_['atoms']
    
    
    _text_ +='\n Atoms #{}\n\n'.format( atomstyle)
    
    if atomstyle in ['charge','full']:
        atom_shape = ' {}'*3+' {:7.4f}'*4+' # {}\n'# idx mol atype charge x y z
    elif atomstyle in ['bond','angle','molecular']:
        atom_shape = ' {0} {1} {2} {4:7.4f} {5:7.4f} {6:7.4f} # {7}\n'
    elif atomstyle =='atomic':
        atom_shape = ' {0} {2} {4:7.4f} {5:7.4f} {6:7.4f} # {7}\n'
        
    base_atoms_n = len( known_atoms)
    for i in range( base_atoms_n):
        aty = known_atoms[i][1]
        _text_ += atom_shape.format( i+1, _mol_[i],
                                    dicts[0][ aty],
                                    float(known_atoms[ i][6]), # charge?? WF
                                    float(_xyz_[i][0])*10,
                                    float(_xyz_[i][1])*10,
                                    float(_xyz_[i][2])*10,
                                    aty
                                   )
    solv_bonds = []
    solv_angles = []
    # asumption: all solvated structures are water??
    # 
    # =============== Solvated topogoly generation ================= #
    TRASH_CAN =  ''' next time better to reccon the structure, the repeating
                    unit, and then get the involved atoms, order, and then 
                    bonds, angles.... get this with the coordinates is another
                    option that probably is going to take longer rt
                 '''
    
    buffer_molnum_pevif = '00000000'
    buffer_moltype_pevif = 'none_type'
    
    if _sidemol_f_ == 1:
        
        charge = _topodata_['S_charge']
        conv_dict = _topodata_['S_translation'] # key s_tag : val l_tag
        
        solv_at_v = range( n_atoms)[ base_atoms_n:]
        #print n_atoms, base_atoms_n, len( _mtype_)
        for i in solv_at_v:
            aty = conv_dict[_atype_[i]] # _atype_ is the atag in TOP
            
            _text_ += atom_shape.format(i+1, _mol_[i], dicts[0][aty],
                                        charge[aty],
                                        float(_xyz_[i][0])*10,
                                        float(_xyz_[i][1])*10,
                                        float(_xyz_[i][2])*10,
                                        aty
                                       )
            
            #write_flag = False
            # meaning new molecule // same type
            if _mol_[i] <> buffer_molnum_pevif:
                buffer_molnum_pevif = _mol_[i]
                # meaning also a new type of molecule
                if _mtype_[i] <> buffer_moltype_pevif:
                    buffer_moltype_pevif = _mtype_[i]
                    new_smol_str = '** New side molecule : {} 1st atom : {} **'
                    print '\n' + new_smol_str.format( _mtype_[i], aty)
                    
                    
                    for sb in range( len( sidemol['tag'])):
                        sidemol['data'][sb]['atoms']
                        if _mtype_[i] == sidemol['tag'][sb]:
                            nm_atn = len( sidemol['data'][sb]['atoms'])
                            print( _mtype_[i]+ '=='+ sidemol['tag'][sb] +'  '+
                                   str(_mtype_[i] == sidemol['tag'][sb]) +'\n'+
                                   str(nm_atn) )
                            #bonds_x_mol = len( sidemol['data'][sb]['bonds'])
                            #angles_x_mol = len( sidemol['data'][sb]['angles'])
                #if write_flag:
                # here is needed something that changes acording to the
                # molecule kind topology
                if nm_atn == 1:
                    pass
                elif nm_atn >= 2:
                    
                    
                    aty2 = conv_dict[ _atype_[i+1]]
                    solv_bonds.append([aty+'-'+aty2, i+1, i+2])
                    
                    
                    if nm_atn == 3:
                        aty3 = conv_dict[ _atype_[i+2]]
                        solv_bonds.append([ aty + '-' + aty3, i+1, i+3])
                        solv_angles.append([aty2 + '-' + aty + '-' + aty3,
                                            i+2, i+1, i+3])
                else:
                    print aty, _mol_[i], buffer_molnum_pevif, i+2, len( _atype_)
                    exit('')
    #########################################################
    '''----------   4th - Chemical topology   ------------'''
    #=======================================================#
    # BULDING AUXILIAR ATOM TAG_ DATA DICTIONARY
    aat_ddic = {}
    if len(atom_info[0]) - minr > 7:
        for i in range( n_atomtypes):
            aat_ddic[ atom_info[i][0]] = atom_info[i][1]
    
    ####################------BONDS------####################
    if _asty_d_[atomstyle]>=2:
        known_bonds = _topodata_['bonds']
        base_bonds_n = len (known_bonds)
        _text_ +='\n Bonds\n\n'
        bond_shape = ' {}'*4+'\n'
        xf = 1
        a_g_d = {} #aux_goofy_dic
        for i in range(base_bonds_n):
            # print known_bonds[i][0], known_bonds[i][1]
            at1 = int(known_bonds[i][0])
            at2 = int(known_bonds[i][1])
            #print at1, at2
            to_print = known_bonds[i][0] +' '+ known_bonds[i][1] +'\n'
            try:
                at1_tag = known_atoms[at1-1][xf]
                at2_tag = known_atoms[at2-1][xf]
                _bond_ty_ = dicts[1][ at1_tag + '-'+ at2_tag]
                
            except KeyError:
                # meaning that is trying with the big name
                try:
                    at1_tag = aat_ddic[ at1_tag]
                    at2_tag = aat_ddic[ at2_tag]
                    _bond_ty_ = dicts[1][ at1_tag + '-'+ at2_tag]
                    
                except KeyError:
                    print to_print
                    print 'Exception {}-{}\n'.format( known_atoms[at1-1][4], 
                                               known_atoms[at2-1][4])
                
            
            _text_ += bond_shape.format( i+1, _bond_ty_, at1, at2)
                        
        if _sidemol_f_ == 1:
            # better way to do this is trough corrds ---------  <WFS>
            for i in range( n_bonds - base_bonds_n):
                _bond_ty_ = dicts[1][ solv_bonds[i][0]]
                _text_ += bond_shape.format(i+1 + base_bonds_n,
                                            _bond_ty_,
                                            solv_bonds[i][1],
                                            solv_bonds[i][2])
    
    
    ####################        ------ANGLES------      #######################
    xf = 1
    if _asty_d_[ atomstyle]>=3:
        known_angles = _topodata_['angles']
        base_angles_n = len(known_angles)
        _text_ +='\n Angles\n\n'
        angle_shape = ' {}'*5+'\n'
        for i in range(base_angles_n):
            
            at1 = int( known_angles[i][0])
            at2 = int( known_angles[i][1])
            at3 = int( known_angles[i][2])
            
            try:
                at1_tag = known_atoms[at1-1][xf]
                at2_tag = known_atoms[at2-1][xf]
                at3_tag = known_atoms[at3-1][xf]
                _angle_ty_ = dicts[2][at1_tag + '-'+ at2_tag+ '-'+ at3_tag]
            except KeyError:
                try:
                    at1_tag = aat_ddic[ at1_tag]
                    at2_tag = aat_ddic[ at2_tag]
                    at3_tag = aat_ddic[ at3_tag]
                    _angle_ty_ = dicts[2][at1_tag + '-'+ at2_tag+ '-'+ at3_tag]
                except KeyError as Er_here:
                    print 'Error ----- '+Er_here.args[0]
                    
            #print angle_t, _angle_ty_
            _text_ += angle_shape.format( i+1, _angle_ty_, at1, at2, at3)
            
        if _sidemol_f_ == 1:
            
            for i in range( n_angles - base_angles_n):
                _angle_ty_ = dicts[2][ solv_angles[i][0]]
                
                _text_ += angle_shape.format( i+1 + base_angles_n,
                                             _angle_ty_,
                                             solv_angles[i][1],
                                             solv_angles[i][2],
                                             solv_angles[i][3]
                                            )
    
    impr_flag = False
    
    ####################        ------DIHEDRAL------       ####################
    if _asty_d_[atomstyle]>=4:
        known_dihedrals = _topodata_['dihedrals']
        base_dihedrals_n = len(known_dihedrals)
        _text_ +='\n Dihedrals\n\n'
        dihedral_shape = ' {}'*6+'\n'
        for i in range(base_dihedrals_n):
            err_str = ''
            at1 = int(known_dihedrals[i][0])
            at2 = int(known_dihedrals[i][1])
            at3 = int(known_dihedrals[i][2])
            at4 = int(known_dihedrals[i][3])
            
            try:
                at1_tag = known_atoms[at1-1][xf]
                at2_tag = known_atoms[at2-1][xf]
                at3_tag = known_atoms[at3-1][xf]
                at4_tag = known_atoms[at4-1][xf]
                _dihe_ty_ = dicts[3][at1_tag + '-'+ at2_tag+ '-'+
                                     at3_tag + '-'+ at4_tag]
            except KeyError:
                try:
                    at1_tag = aat_ddic[ at1_tag]
                    at2_tag = aat_ddic[ at2_tag]
                    at3_tag = aat_ddic[ at3_tag]
                    at4_tag = aat_ddic[ at4_tag]
                    _dihe_ty_ = dicts[3][at1_tag + '-'+ at2_tag+ '-'+
                                     at3_tag + '-'+ at4_tag]
                except KeyError:
                    options = ['X-'+at2_tag+'-'+at3_tag +'-'+at4_tag,
                              at1_tag+'-'+at2_tag+'-'+at3_tag +'-X',
                              'X-' + at2_tag + '-' + at3_tag + '-X',
                              ]
                    for _opt_ in options:
                        try:
                            _dihe_ty_ = dicts[3][ _opt_]
                            break
                        except KeyError:
                            if _opt_ == options[-1]:
                                try:
                                    _dihe_ty_ = dicts[3][ 'X-' + at2_tag[0] +
                                                         'X-'+ at3_tag[0] +
                                                         'X-X']
                                except KeyError as Er_here:
                                    err_str = Er_here.args[0]
            if err_str <> '':
                print 'Atoms {}-{}-{}-{} : '.format( at1, at2, at3, at4),
                print (at1_tag +'-'+ at2_tag+'-'+ at3_tag+'-'+ at4_tag)
                print ( 'Error dihedral ----- '+ err_str +' not found!')
            
            _text_+= dihedral_shape.format( i+1, _dihe_ty_, at1, at2, at3, at4)
    
    ####------ IMPROPERS  -----####
    # TODO SECTION
    if _asty_d_[atomstyle]==5 and impr_flag:
        known_impropers = _topodata_['impropers']
        base_impropers_n = len(known_impropers)
        _text_ +='\n Impropers\n\n'
        improper_shape = ' {}'*6+'\n'
        for i in range(base_impropers_n):
            
            at1 = int(known_impropers[i][0])
            at2 = int(known_impropers[i][1])
            at3 = int(known_impropers[i][2])
            at4 = int(known_impropers[i][3])
            
            _dihe_ty_ = dicts[3][known_atoms[at1-1][1]+'-'
                                 +known_atoms[at2-1][1]+'-'
                                 +known_atoms[at3-1][1]+'-'
                                 +known_atoms[at4-1][1]
                                ]
            _text_+= improper_shape.format( i+1, _dihe_ty_, at1, at2, at3, at4)
            
    return _text_, _flag_
    
def write_lammps_potentials( _topodata_, atomstyle = 'full'):
    ''' writes the potential part in the data file'''
    _flag_ = True
    atom_info = _topodata_['atomtypes'] # index 1: mass ; index 4 -5 : eps-sig
    # unpacking
    _numbers_ = _topodata_['numbers']
    n_atomtypes, n_bondtypes, n_angletypes = _numbers_['type'][:3]
    n_dihedraltypes, n_impropertypes = _numbers_['type'][3:]
    
    #n_bondstypes = len(data_container['bondtypes'])
    
    buckorlj = int( _topodata_[ 'defaults'][0]) # 1 -2 lj/buc
    comb_rule = int( _topodata_[ 'defaults'][1]) # 1-2-3
    
    sigma = []
    epsilon = []
    buck3 = []
    atom_type_d = {}
    # find ptype index, since len can change and the user could put some garbage
    # in between the previous commented line. Eg:
    # ; name  mass charge ptype  V(sigma)  (epsilon) if the comb-rule "2"
    #ptypei = atom_info[0].index('A')
    # Second options second the combination rule, and count from behind:
    minr = 1 - buckorlj # 0 lj and -1 buck
    
    # Any 0 check, to check the feasibility of the conversion to sig and eps
    regular_se = True
    if buckorlj == 1 and comb_rule == 1:
        for x in range( n_atomtypes):
            _A_ = float( atom_info[x][ -1 + minr])
            _B_ = float( atom_info[x][ -2 + minr])
            if _A_ <> 0 and _B_ == 0:
                regular_se = False
                break
    
    for x in range( n_atomtypes):
        #print atom_info[x]
        atom_type_d[atom_info[x][0]] = x+1
        
        _A_ = float( atom_info[x][ -1 + minr])
        _B_ = float( atom_info[x][ -2 + minr])
        
        
        if comb_rule == 1 and regular_se:
            _eps_ = ( _B_**2)/( 4*_A_)
            _sig_ = ( _A_/_B_)**( 1/6.0)
            
        else:
            _eps_ = _A_
            _sig_ = _B_
            
            
        epsilon.append(_eps_ / 4.186)
        
        if buckorlj == 2:#------------------------------------------  <WFS>
            _C_ = float( atom_info[x][ -1])
            buck3.append(' '+ str(f_C_/ 4.186 / (10** 6)))
            sigma.append( 10 / _sig_)
            
        else:
            buck3.append('')
            sigma.append(_sig_* 10)
            
    ####----------- DEFINING LJ INTERACTIONS     ----------####
    #-------------------------------------------------------  <WFS> 
    #                        make function- buck
    '''potential'''
    txt_p_p ='\n Pair Coeffs\n\n'
    for i in range( n_atomtypes):
        txt_p_p +=' {} {} {}{}\n'.format( i+1, epsilon[i], sigma[i], buck3[i])
    
    
    ########    -----------     BOND        ----------     ########
    BondDataBase = ['harmonic','G96','morse','cubic','connection','harmonic',
                    'fene','tabulated','tabulated','restraint']
    Bonds_structures = {'harmonic': {},
                       'morse': {}}
    
    bty =  _topodata_['bondtypes']
    
    bondtypename = BondDataBase[ int(bty[0][2])-1]
    
    txt_p_b ='\n Bond Coeffs #{}\n\n'.format( bondtypename) # bond_style hybrid
    
    blm = len(bty[0]) - 3 # bond length multiplier
    bond_string = ' {}'+ ' {:.4f}'*blm + '\n'
    
    bondtypes_d = {}
    
    for i in range( n_bondtypes):
        extra_end_str = '\n'
        bondtypes_d[ bty[i][0] + '-' + bty[i][1]] = i+1
        bondtypes_d[ bty[i][1] + '-' + bty[i][0]] = i+1
        
        if int(bty[i][2]) <> int(bty[i-1][2]):
            wr_str = 'More than one bond type than {}'
            pop_wrg_1( wr_str.format( bondtypename) )
            _flag_ = False
            
        elif int(bty[i][2]) == 1:
            info_cont = [ i+1,
                          float( bty[i][4])/ 100/ 4.186/2,
                          float( bty[i][3])*10 ]
        elif int(bty[i][2]) == 3:
            extra_end_str = ' {:.4f}\n'
            info_cont = [ i+1,
                         float( bty[i][4])/ 100/ 4.186/2,
                         float( bty[i][5])/10,
                         float( bty[i][3])*10 ]
        else:
            wr_str = 'Bond type {} not implemented yet!'
            pop_wrg_1( wr_str.format( bondtypename) )
            info_cont = [ i+1, 0, 0 ]
            _flag_ = False
        txt_p_b += ( ' {} {:.4f} {:.4f}' + extra_end_str).format( *info_cont)
    
    
    ########    -----------     ANGLE      ----------     ########
    AngleDataBase = ['harmonic','G96','cross bond-bond','cross bond-angle',
                     'charmm','quartic angle','','tabulated'] 
    
    aty = _topodata_['angletypes']
    angletypename = AngleDataBase[ int(aty[0][3])- 1]
    
    txt_p_a ='\n Angle Coeffs #{}\n\n'.format( angletypename)
    
    angletypes_d = {}
    i=0
    info_cont = []
    for i in range( n_angletypes):
        extra_end_str = '\n'
        angletypes_d[aty[i][0]+'-'+aty[i][1]+'-'+aty[i][2]]= i+1
        angletypes_d[aty[i][2]+'-'+aty[i][1]+'-'+aty[i][0]]= i+1
        if int(aty[i][3]) <> int(aty[i-1][3]):
            wr_str = 'More than one angle type than {}'
            pop_wrg_1( wr_str.format( angletypename) )
            _flag_ = False
            
        elif int(aty[i][3]) == 1:
            info_cont = [ i+1,
                         float(aty[i][5])/ 4.186/2,
                         float(aty[i][4]) ]
        elif int(aty[i][3]) == 5:
            extra_end_str = ' {:.4f} {:.4f}\n'
            info_cont = [ i+1,
                         float(aty[i][5])/ 4.186/2,
                         float(aty[i][4]),
                         float(aty[i][7])/ 4.186/2,
                         float(aty[i][6])*10 ]
        else:
            wr_str = 'Angle type {} not implemented yet!'
            pop_wrg_1( wr_str.format( angletypename) )
            info_cont = [ i+1, 0, 0 ]
            _flag_ = False
        txt_p_a += ( ' {} {:.4f} {:.4f}' + extra_end_str).format( *info_cont)
    
    # >===========================================================< #
    ########    -----------     DIHEDRAL      ----------     ########
    DihedralDataBase = [ 'charmm', 'improper', 'opls', # opls<RyckaertBellemans
    # Not implemented ones:
                         'periodic','tabulated'] 
    # asuming that impropers can not be here, purged previously in gromacs.py
    dty = _topodata_['dihedraltypes']
    dihe_kind_names = _topodata_['dihe_kinds'] # set with numbers as string
    
    dihedtypename = []
    if len( dihe_kind_names) > 1:
        dihedtypename.append( 'hybrid')
        _ddb_ = DihedralDataBase[:]
        for d in range( len(_ddb_)):
            _ddb_[d] = ' '+ _ddb_[d]
    else:
        _ddb_  = ['',]*len( DihedralDataBase)
    for di in dihe_kind_names:
        dihedtypename.append( DihedralDataBase[ int( di)- 1])
    
    txt_p_d = ''
    if dihedtypename <> []:
        txt_p_d ='\n Dihedral Coeffs #{}\n\n'.format( dihedtypename[0])
    
    rb_warning = (' Ryckaert-Bellemans angle style conversion in Fourier form' +
                  ' can only be used if LAMMPS was built with the MOLECULE' +
                  ' package!!! quite a base, so this is not printed')
            
    dihedraltypes_d = {} # types dictionary
    i=0
    info_cont = ''
    for i in range( n_dihedraltypes):
        # tag creation
        _type_forward_ = dty[i][0]+'-'+dty[i][1]+'-'+dty[i][2]+'-'+dty[i][3]
        # FIFO type number asigment
        dihedraltypes_d[ _type_forward_ ] = i+1
        ##  need also in backward direction in the lysozyme case
        _type_backward_ = dty[i][3]+'-'+dty[i][2]+'-'+dty[i][1]+'-'+dty[i][0]
        dihedraltypes_d[ _type_backward_] = i+1
        
        _di_ = int(dty[i][4])
        # Charmm / Amber -> coeff_4 = 0.0
        if _di_ == 1:
            info_cont = ( i+1, _ddb_[ _di_ - 1],
                         float(dty[i][6])/4.186/2,
                         int(float(dty[i][7])),
                         int(float(dty[i][5])),
                         '0.0'
                        )
        # Ryckaert-Bellemans
        elif _di_ == 3:
            C0 = float(dty[i][5])
            C1 = float(dty[i][6])
            C2 = float(dty[i][7])
            C3 = float(dty[i][8])
            C4 = float(dty[i][9])
            C5 = float(dty[i][10])
            
            info_cont = ( i+1, _ddb_[ _di_ - 1],
                         ( -2*C1 - (3/2)*C3)/4.186,#K1
                         '{:.4f}'.format( (-C2 - C4)/4.186),#K2
                         '{:.4f}'.format( (-(1/2)*C3)/4.186),#K3
                         '{:.4f}'.format( (-(1/4)*C4)/4.186) #K4
                        )
        else:
            wr_str = 'Dihedral type {} not implemented yet!'
            pop_wrg_1( wr_str.format( DihedralDataBase[ _di_- 1]))
            info_cont = ( i+1, _ddb_[ _di_ - 1],0,0,0,0)
            _flag_ = False
            break
            
        ### TODO :
        #       Optimize here and there, special care with the string handling.
        #       Create a ordered type list if there is more than one kind_
        #       of dihedral.
        txt_p_d += ' {}{} {:.4f} {} {} {}\n'.format( *info_cont)
        
    # === for cycle end
    
    ########    ---------    Final selector section   ----------     ########
    #bad_sty = [ bondtypename, angletypename, dihedtypename]
    if atomstyle in ['full', 'molecular']:
        dicts = [ atom_type_d, bondtypes_d, angletypes_d, dihedraltypes_d]
        txt_p_ = txt_p_p + txt_p_b + txt_p_a + txt_p_d
    elif atomstyle == 'angle':
        dicts = [ atom_type_d, bondtypes_d, angletypes_d]
        txt_p_ = txt_p_p + txt_p_b + txt_p_a
    elif atomstyle == 'bond':
        dicts = [ atom_type_d, bondtypes_d]
        txt_p_ = txt_p_p + txt_p_b
    elif atomstyle == 'atomic' or atomstyle == 'charge':
        dicts = [atom_type_d]
        txt_p_ = txt_p_p
    else:
        print ('\nWeird thing, it is supposed impossible to reach this place\n')
        _flag_ = False
        
        
    return txt_p_, dicts, _flag_


def write_lammps_input(  _simconfig_, _topodata_= None, in_name= 'in.gro2lam'):
    ''' _simconfig_ contains the data gathered from the gui
        _topodata_ comes from the converted gromacs file
        in_name is intended as name for the input to create'''
    
    #================================================================
    '''===========   Gathering and ordering the data   ==========='''
    #================================================================
    
    #===================================================
    ####-----------    SIM RAW CONFIG       --------####
    
    _simconfig_ = _simconfig_[:]
    ( data_file, timestep, nve_steps, nvt_steps, nvt_tss,
    nvt_tdamp, npt_steps, npt_pss, npt_pdamp, npt_tss,
     npt_tdamp) = _simconfig_[0]
    
    nvt_tstart, nvt_tend = nvt_tss.split(':')
    npt_pstart, npt_pend = npt_pss.split(':')
    npt_tstart, npt_tend = npt_tss.split(':')
    
    #print (data_file, timestep, nve_steps, nvt_steps, nvt_tstart, nvt_tend,
    #nvt_tdamp, npt_steps, npt_pstart, npt_pend, npt_tdamp, npt_tdamp,
    #npt_ystart, npt_yend)
    
    i = 5
    thermo, atommap, pairwiseint, lj_rcutoff, c_rcutoff = _simconfig_[1][ :i]
    neighbordistance, lrsolver, lrerror = _simconfig_[1][ i:i+3]
    lj12_13_14, co12_13_14 = _simconfig_[1][ i+3: i+5]
    neighbordelay, neighborupdate, npt_kind = _simconfig_[1][ i+5:i+8]
    f_comb_rule, T_init_vel, f_min_tol, _order_ = _simconfig_[1][ i+8:i+12]
    shake_tol, shake_bn, shake_an = _simconfig_[1][ i+12:]
    
    #===================================================
    ####------------    RESTRAIN DATA       --------####
    
    rest_line = ''
    group_lines = ''
    torestrain = []
    ens_af = []
    if _simconfig_[2] <> []:
        g_names, g_aids, k_xyz_c, runs_c, ch_init = _simconfig_[2][0][:]
        if _simconfig_[2][1] <> None:
            ####### ------------------------------------ Super interesante!!
            ##              este es uno de esos casos donde no es posible 
            ##              utilizar += a pesar de desligar con [:] ... 
            
            aux1, aux2, aux3, aux4, aux5 = _simconfig_[2][1][:] 
            g_names = g_names + aux1
            g_aids  = g_aids  + aux2
            k_xyz_c = k_xyz_c + aux3
            runs_c  = runs_c  + aux4
            ch_init = ch_init + aux5
        print'\n'
        for re in range(len(g_names)):
            if ch_init[re]==1:
                print 'Restraining group '+g_names[re]+' in '+runs_c[re]
                groupinfo = [g_names[re], g_aids[re]]
                group_lines += 'group {} id {}\n'.format( *groupinfo)
                
                if runs_c[re] not in ['', 'No', 'no', '0']:
                    ens = [int(x)-1 for x in runs_c[re].split('-')]
                    torestrain.append( [g_names[re], k_xyz_c[re], ens ])
                
                    for e in ens:
                        if e not in ens_af:
                            ens_af.append(e)
        if group_lines <> '':
            group_lines +='\n'
    
    mix_value = {'1':'geometric', '2':'arithmetic',
                 '3':'geometric', '4':'sixthpower'}
    
    
    #for mt in range(len( _mtype_)):
        #group_lines += 'group {} id {}:{}\n'.format(*_mtype_[mt])
    _asty_d_ ={ 'atomic':1, 'charge':2, 'bond':3, 'angle':4,
                'full':6, 'molecular':6}
    
    #===================================================
    ####------------      TOPO DATA         --------####
    
    print '\n'+data_file + '\n'
    if _topodata_ <> None:
        atomstyle_o, _solvated_, _autoload_ = _topodata_['config'] 
        _, comb_rule, _, _, _ = _topodata_['defaults']
        
    else:
        print '**** Without _topodata_ !!'
        atomstyle_o = ''
        comb_rule = ''
        
    ## -------------------------- getting styles
    _aux_here = get_style_info( data_file)
    print _aux_here
    atomstyle, bondstyle, anglstyle, dihestyle, imprstyle = _aux_here
    if atomstyle_o <> '' and atomstyle_o <> atomstyle[0]:
        pop_wrg_1( 'Incongruence between atom styles!')
        print atomstyle_o, atomstyle[0]
    
    ## ---------------- MIXING RULE
    if f_comb_rule in mix_value.values():
        mix_value_s=' mix '+f_comb_rule
    elif f_comb_rule=='from_gromacs' and _topodata_<>None:
        mix_value_s=' mix '+mix_value[comb_rule]
    else:
        print 'Using default mixing rule'
        mix_value_s = ''
        

    #================================================================
    '''===========   Writing Lammps input command file  =========='''
    #================================================================
    _dtxt_= '# Generated with Gro2lam\n\n'+'units real\nboundary p p p\n'
    # as I understand lammps default is 3
    #_dtxt_+= '%s %d\n'.format('dimension',dimension)
    _dtxt_+= 'atom_style '+atomstyle[0]+'\n'
    if atomstyle[0] not in ['full', 'charge]']: # no charges
        if 'coul' in pairwiseint:
            pairwiseint = pairwiseint.split('/coul')[0]
        c_rcutoff = ''
    elif 'coul' not in pairwiseint:
        c_rcutoff = ''
        
    if pairwiseint == 'zero':
            c_rcutoff = 'nocoeff'
        
    _dtxt_+= '\natom_modify map {}\n'.format( atommap)
    #===================================================
    ####------------  SYSTEM CONFIGURATION  --------####
    
    ###############    TODO_WF this for sure can be improved----------- please!
    # options like full and non bonded interactions could be asked by the user
    _dsc_txt=['pair_style {} {}'.format( pairwiseint, lj_rcutoff)]
    _dsc_txt.append(' {}\n'.format( c_rcutoff))
    if bondstyle[0] <> '':
        _dsc_txt.append( 'bond_style '+' '.join( bondstyle)+'\n')
    if anglstyle[0] <> '':
        _dsc_txt.append( 'angle_style '+' '.join( anglstyle)+'\n')
    if dihestyle[0] <> '':
        _dsc_txt.append( 'dihedral_style '+' '.join( dihestyle)+'\n')
    if imprstyle[0] <> '':
        _dsc_txt.append( 'improper_style '+' '.join( imprstyle)+'\n')
    _dtxt_+= ''.join(_dsc_txt[:_asty_d_[atomstyle[0]]])+'\n'
    
    
    if 'data' in data_file:
        _dtxt_+= 'read_data {}\n'.format(data_file)
    else:
        _dtxt_+= 'read_restart {}\n'.format(data_file)
    
    #===================================================
    ####--------------   NEIGHBOR LIST   -----------####
    
    _dtxt_+= '\nneighbor {} bin\n'.format( neighbordistance)
    
    if lrsolver <> '' and atomstyle[0] in ['full','charge']:
        if '/coul/long' in pairwiseint:
            _dtxt_+= 'kspace_style {} {}\n'.format( lrsolver, lrerror)
        
        aux_here1 = lj12_13_14.split(':')
        if lj12_13_14 == co12_13_14:
            sp_bon_3 = ['/coul {}'.format( aux_here1[0])] + aux_here1[1:]
        else:
            aux_here2 = co12_13_14.split(':')
            aux_here1 += [ aux_here2[0]]
            aux_txt = ' {} {} {} coul {}'.format( *aux_here1)
            sp_bon_3 = [ aux_txt] + aux_here2[1:]
                            
    elif lrsolver <> '':
        sp_bon_3 = lj12_13_14.split(':')
        
    
    if lrsolver <> '':
        _dtxt_+= 'special_bonds lj{} {} {}\n'.format( *sp_bon_3)
        
    _dtxt_+= 'pair_modify shift no tail yes'+mix_value_s+'\n'
    
    _aux_s_ = 'neigh_modify every {} delay {} check yes\n\n'
    _dtxt_+= _aux_s_.format( neighborupdate, neighbordelay)
    
    #===================================================
    ####---------------  TIMESTEP   ----------------####
    _dtxt_+= 'timestep {}\n\n\n'.format(timestep)
    _dtxt_+= 'thermo {}\n'.format(thermo)
    _dtxt_+= ('thermo_style custom step temp press vol '
              +'epair emol etotal enthalpy'
              +'\n\n')
    
    #===================================================
    ####--------------  Init VELOCITIES   ----------####
    aux_vel_str = 'velocity all create {} 1234567 rot yes dist gaussian\n\n'
    _dtxt_+= aux_vel_str.format(T_init_vel)
    
    #===================================================
    ####----------------   GROUPS   ----------------####
    _dtxt_+= group_lines
    
    #===================================================
    ####---------------     SHAKE       ------------####
    shake_bn, shake_an
    shake_txt = 'fix shake_name1 all shake {} 20 0'.format( shake_tol)
    print shake_bn, shake_an
    if shake_bn <> '0' or shake_an <> '0':
        
        if shake_bn <> '0':
            shake_txt += ' b'
            shake_bn = shake_bn.split('-')
            for bn in range(len(shake_bn)):
                shake_txt += ' '+shake_bn[bn]

        if shake_an <> '0':
            shake_txt += ' a'
            shake_an = shake_an.split('-')
            for an in range(len(shake_an)):
                shake_txt += ' '+shake_an[an]
        _dtxt_+= shake_txt+'\n\n'
    
    #===================================================
    ####---------------   SIMULATION    ------------####
    ensembles = _order_.split('-')
    curr_time = 0
    timestep = float(timestep)
    
    tounfix = [[],[]]
    _dtxt_ += '\n'
    for en in range(len(ensembles)):
        
        
        if ens_af<>[] and en in ens_af: #       RESTRAIN 
            
            for re in range(len(torestrain)):
                if en in torestrain[re][2]:
                    
                    if en-1 not in torestrain[re][2]:
                        spring_f = 'fix rest_{0}_{1} {0} spring/self {2} {3}\n'
                        k, xyz = torestrain[re][1].split(':')
                        _dtxt_ += spring_f.format( torestrain[re][0], en+1 ,
                                                  k, xyz)
                        unr= 0+en
                        while unr+1 in torestrain[re][2]:
                            unr+=1
                        
                        name_2uf = 'rest_{0}_{1}'.format( torestrain[re][0],
                                                         en+1)
                        tounfix= [ tounfix[0]+ [unr], tounfix[1]+ [name_2uf]]
            _dtxt_ += '\n'
            
        if ensembles[en]=='NVE' and nve_steps <> '' and nve_steps.isdigit():
            steps = int(nve_steps)
            nve_frm = 'fix nve_name1 all nve\nrun {}\nunfix nve_name1\n\n'
            _dtxt_ += nve_frm.format(steps)
            curr_time += steps*timestep
        
        elif ensembles[en]=='NPT' and npt_steps <> '' and npt_steps.isdigit():
            steps = int(npt_steps)
            npt_frm = 'fix npt_name1 all npt temp {} {} {} {} {} {} {}\n'
            _dtxt_ += npt_frm.format( npt_tstart, npt_tend, npt_tdamp,
                                     npt_kind, npt_pstart, npt_pend, npt_pdamp)
            _dtxt_+= 'run {}\nunfix npt_name1\n\n'.format( steps)
            curr_time += steps*timestep
        
        elif ensembles[en]=='NVT' and nvt_steps <> '' and nvt_steps.isdigit():
            steps = int(nvt_steps)
            nvt_frm = 'fix nvt_name1 all nvt temp {} {} {}\n'
            _dtxt_ += nvt_frm.format( nvt_tstart, nvt_tend, nvt_tdamp )
            _dtxt_+= 'run {}\nunfix nvt_name1\n\n'.format( steps)
            curr_time += steps*timestep
        
        elif ensembles[en]=='R':
            restart_txt = '\nwrite_restart restart.g2l_{}fs\n'
            _dtxt_ += restart_txt.format(int(curr_time))
            
        elif ensembles[en]=='M':
            if float(f_min_tol) > 1.0e-3:
                e_min_tol = 1.0e-2
                f_min_tol = 1.0e-3
            else:
                e_min_tol = float(f_min_tol)*100
            
            emin_frm = 'minimize {} {} 10000 100000\n\n'
            _dtxt_+= emin_frm.format( e_min_tol, f_min_tol )
            
            
        if tounfix <> [ [], []] and en in tounfix[0]: #       UNFIX RESTRAIN
            for unf in range( len( tounfix[0])):
                if tounfix[0][unf] == en:
                    _dtxt_ += 'unfix ' + tounfix[1][unf] + '\n'
    
    print ('Writing Lammps input script...')
    
    write_file( in_name , _dtxt_)
    print_dec_g ('Successful writing!!')
    
    
     #-------------------- here would be optimum some further check
    return True

def get_style_info( lammps_datafile):
    
    #atom_sty, bond_sty, angl_sty, dihe_sty, impr_sty = '', '', '', '', ''
    styles = [ 'Bond', 'Angle', 'Dihedral', 'Improper', 'Atoms' ]
    sty_qty = [0,]*len( styles)
    default_styles = [ 'harmonic', 'harmonic', 'charmm', 'harmonic', 'full']
    sty_container = [ [], [], [], [], []]
    
    def_wrg_str = ( '{} style info not found or missing in the data file!'
                       + 'Using default : {}')
    try:
        
        with open( lammps_datafile, 'r')  as indata:
            
            # types collection
            for k_line in indata:
                line_c =  k_line.split()
                if len (line_c) == 3 and line_c[2] == 'types':
                    for st in range( len( styles)):
                        if line_c[1][1:] in styles[st]:
                            sty_qty[st] = int( line_c[0])
                            break
                elif len (line_c) > 3 and  line_c[2] == 'xlo':
                    break
            print 'Quantities : ', sty_qty
            read_flag = False
            reading_flag = False
            index = 0
            for k_line in indata:
                line_c =  k_line.split()
                #print line_c
                # in cases with hybrid type, it should read from the second 
                # position in the data line of bond, angle, dihedral and impr
                if read_flag:
                    
                    if len( line_c) < 1 and reading_flag:
                        read_flag = False
                        reading_flag = False
                        index += 1
                        while not sty_qty[ index]:
                            sty_container[ index].append( '')
                            index += 1
                        print '... done!'
                    elif len( line_c) < 1 or line_c[0][0] == '#':
                        pass
                    else:
                        reading_flag = True
                        new_sty = line_c[1]
                        if new_sty not in sty_container[ index]:
                            print 'Style : ', styles[ index], ' - ', new_sty,
                            sty_container[ index].append( new_sty)
                    
                # cutting out the crap, normal empty and commented lines
                elif len( line_c) < 1 or line_c[0][0] == '#':
                    pass
                    
                elif  ( styles[ index] == line_c[0] and 
                      ( index == 4 or 'Coeffs' == line_c[1]) ):
                    
                    print index, styles[ index], k_line
                    aux_cont = k_line.split('#')
                    
                    if len( aux_cont) > 1:
                        sty_container[ index].append( aux_cont[1].strip())
                        if sty_container[ index][0] == 'hybrid':
                            read_flag = True
                            index -= 1
                    else:
                        sty_container[ index].append( default_styles[ index])
                        pop_wrg_1( def_wrg_str.format( styles[ index], 
                                                       sty_container[ index]))
                    if index + 1 < len(sty_qty):
                        index += 1
                        while not sty_qty[ index]:
                            sty_container[ index].append( '')
                            index += 1
                    
    except IOError:
        pop_wrg_1( 'Data file not found!')
        print ( 'Maybe try performing a conversion first! ;)')
        _flag_ = False
        
    sty_container = [ sty_container[4],] + sty_container[:4]
    return sty_container

if __name__ == '__main__':
    pass
    
# vim:tw=80
