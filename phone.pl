# -------------------------------------------------------------------- #
#   phone.pl - �������ä���δĶ��ѿ�����Ϥ����ϥå���ؤλ��Ȥ��֤�
# -------------------------------------------------------------------- #
=head1 NAME

phone.pl - �������ä���δĶ��ѿ�����Ϥ����ϥå���ؤλ��Ȥ��֤�

=head1 SYNOPSIS

�ڷ��ӥ���ꥢ��Ƚ�̤��� Location ���Ф���

    require "phone.pl";
    my $phone = &phone_info();

    if ( $phone->{type} eq "docomo" ) {
        if ( $phone->{color} ) {
            print "Location: http://domain.name/i-color.html\n\n";
        } else {
            print "Location: http://domain.name/i-black.html\n\n";
        }
    } elsif ( $phone->{type} eq "jphone" ) {
        print "Location: http://domain.name/j-phone.html\n\n";
    } elsif ( $phone->{type} eq "ezweb" ) {
        print "Location: http://domain.name/ezweb.hdml\n\n";
    } else {
        print "Location: http://domain.name/pc.html\n\n";
    }

=head1 DESCRIPTION

�������ä���Υ�������������դ���CGI�����ˡ��������ä˴ؤ���Ķ��ѿ���
���Ϥ��ơ��Ȥ��䤹�����Υϥå��������������λ��Ȥ��֤��ޤ���
�����Ǥϡ��ʲ��μ��ǥϥå������������ΤȤ��ޤ���

    require "phone.pl";
    my $phone = &phone_info();

�������ò�Ҥ�Ƚ�̤ˤϡ�type �ץ�ѥƥ������Ѥ��ޤ���

    $phone->{type}  ��  �������ò�ҡʥ���ꥢ��

����3����ꥢ�� type �ץ�ѥƥ����ͤϰʲ��Τ褦�ˤʤ�ޤ���

        "docomo"    ��  NTT�ɥ���i�⡼�ɡ�PHS�֥饦���ե����ޤ��
        "jphone"    ��  �ܡ����ե���
        "ezweb"     ��  au��TU-KA EZweb

���� phone.pl �Ȥθߴ��Τ��ᡢ�ܡ����ե���� "jphone" ��Ƚ�̤��ޤ���
��������3����ꥢ��¾�ˡ�PHS �� L �⡼�ɤ�Ƚ�ꤷ�ޤ���

        "astel"     ��  ASTEL dotI
        "ahphone"   ��  AirH" Phone
        "pdx"       ��  P�᡼��DX
        "lmode"     ��  NTT L�⡼��
        ""          ��  PC���ͤ϶��Ǥ���

type �ץ�ѥƥ��ʳ��˻��ȤǤ����ͤϡ��ʲ����̤�Ǥ���

    ��ü������ϡ�
    $phone->{name}          ��  ���ӵ���̾�ʾ���̾�ʤɡ�
    $phone->{code}          ��  ���ӵ���̾�����ʥ����ɤʤɡ�
    $phone->{color}         ��  ���顼ɽ���б��ʥ��顼�῿������ᵶ��
    $phone->{ver}           ��  �С���������
    $phone->{cache}         ��  ����å������̡ʥХ���ñ�̡�
    $phone->{qvga}          ��  QVGA�վ���ܵ����QVGA�῿��
    $phone->{width}         ��  �ǥ����ץ쥤�����������ʥԥ�����ñ�̡�
    $phone->{height}        ��  �ǥ����ץ쥤�����������ʥԥ�����ñ�̡�

�ʲ��Υץ�ѥƥ��ϡ��б�����Ǥ���п��Ȥʤ�ޤ�����ezmovie�������

    �����ɽ���ϡ�
    $phone->{image_jpeg}    ��  JPEG����
    $phone->{image_png}     ��  PNG����
    $phone->{image_gif}     ��  GIF����
    $phone->{image_bmp}     ��  BMP����

    �㲻�������ϡ�
    $phone->{audio_mmf}     ��  ���� .mmf (SMAF)
    $phone->{audio_pmd}     ��  ���� .pmd
    $phone->{audio_smd}     ��  ���� .smd
    $phone->{audio_mld}     ��  ���� .mld
    $phone->{audio_qcp}     ��  ��ܥ��� .qcp (EZ)

    ��ư������ϡ�
    $phone->{movie_amc}     ��  EZ�ࡼ�ӡ� AMC(.amc)
    $phone->{movie_3g2}     ��  EZ�ࡼ�ӡ� 3GPP2(.3g2)

    ��NTT�ɥ���i�⡼�����ѡ�
    $phone->{docomo_foma}   ��  NTT�ɥ���FOMAü��
    $phone->{docomo_pdc}    ��  NTT�ɥ���PDCü��
    $phone->{docomo_phs}    ��  NTT�ɥ���PHSü��

    ��ܡ����ե������ѡ�
    $phone->{vodafone_2g}   ��  �ܡ����ե���PDCü��
    $phone->{vodafone_3g}   ��  �ܡ����ե���3Gü��
    $phone->{disable_post}  ��  method="post" �����Բ�

    ��EZ���������ѡ�
    $phone->{ezweb_mono}    ��  EZ���������HDMLü����au 300�ϡ�1.4KB��
    $phone->{hdml_native}   ��  EZ������HDMLü����au 300��10xx�ϡ�
    $phone->{xhtml_native}  ��  EZ������XHTMLü����au 110x�ϡ���WIN��
    $phone->{ezmovie}       ��  EZ�ࡼ�ӡ��б�������0��9��

����ˤ�äƤϡ��ǥ����ץ쥤�������䥭��å������̤ʤɤ����Τ�
�����Ǥ��ʤ����⤢��ޤ����ʤ��ξ����ͤϵ��Ȥʤ�ޤ���
�ޤ������¤�����ޤ��� UID�ʷ���ü����ͭ����ˤ�����Ǥ��ޤ���

    $phone->{uid}           ��  UID�ʷ���ü����ͭ�����

����������⡼�ɵ��Ǥϸ��������ȤΥɥᥤ�󲼤ǤΤ߼�����ǽ��
�ܡ����ե��󵡤Ǥϡ����������Ȥ� pid��sid ���ѻ��Τ߼�����ǽ��
�ţڥ����ֵ���Ǥϡ����������ꥵ������鷺������ǽ�Ǥ���
�ʤ����գɣĤϺ��β�ǽ�Τ��ᡢ��긷̩�˸���Ƚ�̤�Ԥ�����ˤ�
�ǣץ��󥿣ɣХ��ɥ쥹�ˤ�륢���������¤�ʻ�Ѥ�ɬ�פǤ���

=head1 COMMENT

phone.pl �Ϥ���ͳ�ˤ��Ȥ�����������
���ո����Х�����ʤɤ��Ԥ����Ƥ���ޤ���

=head1 VERSIONS

    Version 1.01 (2000/05/11) �ǽ�ΥС������
    Version 1.02 (2000/05/12) ezWeb ����̾�Ѵ��б���DoCoMo �Х��ե��å���
    Version 1.03 (2001/02/19) DoCoMo ����̾�� i �ޤ��դ���
    Version 1.04 (2001/04/05) DoCoMo �ǿ������б��������ƥ��б�
    Version 1.10 (2002/03/25) au �ǿ������б����ե����륿���׼¸��б�
    Version 1.11 (2002/04/26) DoCoMo ������Ƚ���б�
    Version 1.12 (2002/05/07) DoCoMo FOMA��au �����TK11��C313K �����б�
    Version 1.13 (2002/09/30) au �����audio/vnd.qcelp �����б�
    Version 1.14 (2002/10/08) au ��ưȽ����������
    Version 1.15 (2002/11/04) au �������б���SA22��A3015SA��
    Version 1.17 (2002/11/27) au �������б���A5303H��A5302CA��TT22��
    Version 1.18 (2002/11/28) hdml_native/xhtml_native/disable_post
    Version 1.19 (2002/11/28) hdml_native/xhtml_native ����
    Version 1.20 (2002/12/06) au �������б���A1101S/TK21/TK22�ˡ�TK03 ��MMF�б�
    Version 1.21 (2003/04/16) au �������б���A1301S/A1302SA/TK31/TS31��
    Version 1.22 (2003/04/17) au �������б���TK23/A5402ST�ˡ�A5402ST �Ͽ�¬
    Version 1.30 (2003/05/02) uid ������ǽ�����¤����
    Version 1.32 (2003/06/10) DDI Pocket AirH" Phone�б���AH-J3001V/AH-J3002V��
                              au �������б���A5402S/A5401CA/A5306ST/A5305K��
                              ��A5402ST �ϸ��ǡ��������� A5306ST �Ǥ�����
    Version 1.33 (2003/07/01) DOCOMO_GLAY �Х�����(����?)
    Version 1.34 (2003/08/01) au �������б���A5303H-II/A1304T/TT31��
    Version 1.35 (2003/08/17) au �������б���A1401K/A1303SA��
                              au ������������ＫưȽ���ɲá�ezweb_mono��
                              au �ϰ��Ҽ�ưȽ���ɲ� (ezweb_area)
                              DoCoMo (docomo_foma docomo_pdc docomo_phs)�ɲ�
    Version 1.36 (2003/09/17) au �������б� (A5307ST/A5501T/W11H)
    Version 1.37 (2003/10/23) DoCoMo JPEG Ƚ���б���image_jpeg��
                              au ����̾�ѹ���A5307ST��INFOBAR��
    Version 1.38 (2003/10/26) DoCoMo ��ܥ������б�����Ƚ��(docomo_voice)
    Version 1.39 (2004/02/06) DoCoMo 900i ���꡼���б�
    Version 1.40 (2004/02/13) au/TU-KA �������б���W11K¾��
    Version 1.41 (2004/03/08) DoCoMo ��ĥ��ʸ�����б�����Ƚ��(docomo_std_emoji)
    Version 1.42 (2004/03/16) au/TU-KA �������б���A5405SA¾��
    Version 1.43 (2004/06/29) DoCoMo �ǥ����ץ쥤������Ƚ���ɲ�
                              (3����ꥢ���Ƽ�����ǽ:width:height)
                              au/TU-KA �������б���A5506T¾��
    Version 1.44 (2004/07/26) DoCoMo QVGA �������б���F880iES¾��
    Version 1.45 (2004/09/17) DOCOMO_QVGA ����
    Version 1.46 (2004/09/28) au/TU-KA �������б���A5504T��A1305SA¾��
    Version 1.47 (2004/10/19) i�⡼��HTML���ߥ�졼��II��QVGA�б�
    Version 1.48 (2004/11/09) EZ�ࡼ�ӡ� ezmovie��movie_amc��movie_3g2
    Version 1.49 (2004/12/01) QVGA����β�����240�ԥ����롢EZ�������б�
    Version 1.50 (2004/12/22) i�⡼��HTML���ߥ�졼��7.0��16�ӥåȥե���ȴ���
    Version 1.51 (2005/01/05) �ɥ���700i���꡼���б�
    Version 1.52 (2005/01/17) Vodafone ����å�������Ƚ���ѹ���W21CA�б�
    Version 1.53 (2005/01/26) Vodafone V902SH¾����3G�����б�
    Version 1.54 (2005/01/26) Vodafone 702MO �б���MOT-V980��
    Version 1.55 (2005/01/31) Vodafone �С�������ֹ�Ƚ��Х�����
    Version 1.56 (2005/02/02) Vodafone 3G���Ӥ� 300KB����å���Ȥߤʤ�
    Version 1.57 (2005/02/18) au �������б���W31SA��
    Version 1.58 (2005/03/22) au/TU-KA �������б���PENCK/TT51��
    Version 1.59 (2005/03/28) au �������б���W31K/W31S��
    Version 1.60 (2005/03/30) au Ƚ�̥Х�������W31K/W31S�ˡ�POD����
    Version 1.61 (2005/06/04) au �������б���Sweets��
    Version 1.62 (2005/06/18) ư���б�����Ƚ�̡�Thanks to MIZUNOTOMOAKI��
    Version 1.63 (2005/06/20) movie_3g2 Ƚ�̾�､��
    Version 1.64 (2005/09/03) SO213iS Ƚ�̽�����SH851i �б���au �������б�
    Version 1.65 (2005/09/27) au �������б���Thanks to IIJIMA��
    Version 1.66 (2006/02/21) au �������б���W41K/Sweets pure¾��

=head1 SEE ALSO

    http://www.kawa.net/works/perl/phone/pnews.html
    http://www.nttdocomo.co.jp/p_s/imode/spec/ryouiki.html
    http://www.au.kddi.com/ezfactory/tec/spec/4_4.html
    http://developers.vodafone.jp/dp/tool_dl/web/useragent.php

=head1 AUTHOR

Copyright 2000-2006 Kawasaki Yusuke <u-suke [at] kawa.net>

=cut
# -------------------------------------------------------------------- #
    use strict;
# -------------------------------------------------------------------- #
#   NTT DoCoMo i-mode ������δ��ξ����depth��
#   i-mode �ϴ���Ū�˵���̾������å������̰ʳ��δĶ��ѿ�������ޤ���
#   ���Τ���ɬ�פʾ���ϼ������ݻ�����ɬ�פ�����ޤ������ؤ��ʤ���
# -------------------------------------------------------------------- #
    my $DOCOMO_DEFAULT_DEPTH = 8;       # ɸ��� depth
    # �������Ĵ����
    my $DOCOMO_BLACK = [qw(
        D501i       ER209i      F501i       N501i
        NM502i      R209i       P501i
    )];
    # �������Ĵ����
    my $DOCOMO_GLAY = [qw(
        N209i       N502i       N821i       P209i
        P502i       P821i       R691i       SO502i
    )];
    # �忮���ǥ� .mld ���б������NM502i���������¤����˸�������
    my $DOCOMO_NO_MLD = [qw(
        D501i       F501i       N501i       P501i       NM502i
    )];
    # ��ܥ��� .mld ���б�����
    my $DOCOMO_NO_VOICE = [qw(
        D501i   F501i   N501i   P501i   NM502i
        D209i   D502i   ER209i  F209i   KO209i  N209i
        N502i   N502it  N821i   P209i   P209is  P502i
        P821i   R209i   R691i   SH821i  SO502i  SO502iWM
        F502i   F502it
        D503i   D503iS  D210i   D2101V
        P503i   P503iS
        SO503i  SO503iS SO210i  SO211i
        P210i
        P2101V
        KO210i
        T2101V
    )];
    # JPEG ���б�����ΰ����ʺ���ε�����б���
    # P503i ���б������������˥Х������뤿�ᡢ���б��Ȥߤʤ�
    my $DOCOMO_NO_JPEG = [qw(
        D501i   F501i   N501i   P501i
        D502i   F502i   N502i   P502i   SO502i  NM502i
        F502it  N502it  SO502iWM
        D503i   F503i   SO503i  P503i
        D503iS  F503iS  SO503iS
        D209i   F209i   KO209i  N209i   P209i   R209i   ER209i
        P209is
        D210i   F210i   KO210i  N210i   P210i   SO210i
        D211i   F211i
        F671i   R691i   R692i
        N821i   P821i   SH821i
    )];
    # i�⡼�����FOMA�Τ���MP4���б��������
    my $DOCOMO_NO_MP4 = [qw(
        N2001     N2002     P2002   D2101V    P2101V
        SH2101V   T2101V
    )];
    # i�⡼�����FOMA�Τ���ASF�б�����ʵ�����ʤΤǷ���Ǥ���
    my $DOCOMO_ASF = [qw( D2101V SH2101V T2101V )];

    # XHTML��FOMA�Τ���XHTML���б�����
    my $DOCOMO_NO_XHTML = [qw(
        N2001     N2002     P2002   D2101V    P2101V
        SH2101V   T2101V
    )];
# -------------------------------------------------------------------- #
#   i�⡼���б�HTML�С������(1.0��3.0�ޤ�)
# -------------------------------------------------------------------- #
    my $DOCOMO_HTML1 = [qw(
        D501i   F501i   N501i   P501i
    )];
    my $DOCOMO_HTML2 = [qw(
        D502i   F502i   N502i       P502i   NM502i  SO502i
        F502it  N502it  SO502iWM    SH821i  N821i   P821i
        D209i   ER209i  F209i       KO209i  N209i   P209i
        P209is  R209i   R691i       F210i   N210i   P210i
        KO210i  F671i
    )];
    my $DOCOMO_HTML3 = [qw(
        D210i   SO210i  F503i   F503iS  P503i   P503iS
        N503i   N503iS  SO503i  SO503iS D503i   D503iS
        F211i   D211i   N211i   N211iS  P211i   P211iS
        SO211i  R211i   SH251i  SH251iS R692i   N2001
        N2002   D2101V  P2101V  SH2101V T2101V
    )];
    my $DOCOMO_HTML4 = [qw(
        D504i   F504i   F504iS  N504i   N504iS  SO504i  P504i   P504iS
        D251i   D251iS  F251i   N251i   N251iS  P251iS
        F671iS
        F212i   SO212i
        F661i
        F672i
        SO213i  SO213iS
        F2051   N2051
        P2102V  F2102V  N2102V
        N2701
    )];
# -------------------------------------------------------------------- #
#   DOCOMO�ǥ����ץ쥤������
#   http://www.nttdocomo.co.jp/mc-user/i/spec/ryouiki.html
# -------------------------------------------------------------------- #
    my $DOCOMO_DISPLAY = {
        'F901iS'      => '240x320',
        'SH901iS'     => '240x320',
        'D901iS'      => '240x320',
        'N901iS'      => '240x320',
        'P901iS'      => '240x320',
        'D901i'       => '240x320',
        'F901iC'      => '240x320',
        'N901iC'      => '240x320',
        'P901i'       => '240x320',
        'SH901iC'     => '240x320',

        'F900i'       => '240x320',
        'N900i'       => '240x269',
        'P900i'       => '240x266',
        'SH900i'      => '240x320',
        'F900iT'      => '240x320',
        'F900iC'      => '240x320',
        'P900iV'      => '240x266',
        'D900i'       => '240x320',
        'N900iG'      => '240x269',
        'N900iS'      => '240x269',
        'N900iL'      => '240x269',

        'F700i'       => '240x320',
        'N700i'       => '240x320',
        'P700i'       => '240x320',
        'SH700i'      => '240x320',

        'F880iES'     => '240x320',

        'F2051'       => '176x182',
        'N2051'       => '176x198',
        'P2102V'      => '176x198',
        'F2102V'      => '176x182',
        'N2102V'      => '176x198',
        'N2701'       => '176x198',
        'N2001'       => '120x130',
        'N2002'       => '120x130',
        'P2002'       => '120x130',
        'D2101V'      => '132x142',
        'P2101V'      => '176x164',
        'SH2101V'     => '320x240',
        'T2101V'      => '176x144',

        'D506i'       => '240x320',
        'F506i'       => '240x268',
        'N506i'       => '240x320',
        'N506iS'      => '240x320',
        'P506iC'      => '240x320',
        'SH506iC'     => '240x320',
        'SO506iC'     => '240x320',
        'SO506i'      => '240x320',       # premini-II
        'SO506iS'     => '240x320',       # premini-IIS

        'D505i'       => '240x320',
        'SO505i'      => '256x320',
        'SH505i'      => '240x320',
        'N505i'       => '240x320',
        'F505i'       => '240x268',
        'P505i'       => '240x320',
        'D505iS'      => '240x320',
        'P505iS'      => '240x320',
        'N505iS'      => '240x320',
        'SO505iS'     => '240x320',
        'SH505iS'     => '240x320',
        'F505iGPS'    => '240x268',

        'D504i'       => '132x160',
        'F504i'       => '132x136',
        'F504iS'      => '132x136',
        'N504i'       => '160x198',
        'N504iS'      => '160x198',
        'SO504i'      => '128x128',
        'P504i'       => '132x144',
        'P504iS'      => '132x176',

        'F503i'       => '120x130',
        'F503iS'      => '120x130',
        'P503i'       => '120x115',
        'P503iS'      => '120x115',
        'N503i'       => '120x130',
        'N503iS'      => '120x130',
        'SO503i'      => '120x120',
        'SO503iS'     => '120x120',
        'D503i'       => '132x142',
        'D503iS'      => '132x142',

        'D502i'       => '96x64',
        'F502i'       => '96x78',
        'N502i'       => '118x70',
        'P502i'       => '96x95',
        'NM502i'      => '95x76',
        'SO502i'      => '120x72',
        'F502it'      => '96x78',
        'N502it'      => '118x70',
        'SO502iWM'    => '120x120',

        'P501i'       => '96x95',

        'D253i'       => '176x240',
        'N253i'       => '160x198',
        'P253i'       => '132x176',
        'D253iWM'     => '220x176',       # Music PORTER
        'P253iS'      => '132x176',       # Lechiffon

        'D252i'       => '176x240',
        'SH252i'      => '240x320',
        'P252i'       => '132x176',
        'N252i'       => '132x158',
        'P252iS'      => '132x176',

        'D251i'       => '132x160',
        'D251iS'      => '132x160',
        'F251i'       => '132x144',
        'N251i'       => '132x158',
        'N251iS'      => '132x158',
        'P251iS'      => '132x176',
        'SH251i'      => '120x130',
        'SH251iS'     => '176x187',

        'SO213i'      => '128x128',       # premini
        'SO213iS'     => '128x128',       # premini-S (thanx to PICPIC)
        'P213i'       => '132x176',       # prosolid

        'F212i'       => '132x156',
        'SO212i'      => '128x128',

        'F211i'       => '96x113',
        'D211i'       => '100x120',
        'N211i'       => '120x145',
        'N211iS'      => '120x145',
        'P211i'       => '120x130',
        'P211iS'      => '120x130',
        'SO211i'      => '120x120',
        'R211i'       => '96x113',

        'F210i'       => '96x113',
        'N210i'       => '120x127',
        'P210i'       => '96x91',
        'KO210i'      => '96x96',
        'D210i'       => '96x91',
        'SO210i'      => '120x113',

        'D209i'       => '96x120',
        'ER209i'      => '120x72',
        'F209i'       => '96x78',
        'KO209i'      => '96x96',
        'N209i'       => '108x54',
        'P209i'       => '96x91',
        'P209iS'      => '96x91',
        'R209i'       => '96x72',

        'SH821i'      => '96x78',
        'N821i'       => '118x70',
        'P821i'       => '118x70',

        'P651ps'      => '96x91',
        'R691i'       => '96x72',
        'F671i'       => '120x126',
        'R692i'       => '96x113',
        'F671iS'      => '160x120',
        'F661i'       => '132x156',
        'F672i'       => '160x120',

        'ISIM0101'    => '240x320',       # ���ߥ�졼��II
      };
# -------------------------------------------------------------------- #
#   ezWeb �����ɢ�����̾�Ѵ�ɽ
#   http://www.au.kddi.com/ezfactory/tec/spec/4_4.html
# -------------------------------------------------------------------- #
    my $EZWEB_NAME = { reverse qw(
        UP.SDK  UPG     UP.SDK  NT95

        W41K    KC35    W41SA   SA36
        W41T    TS34    W41H    HI36
        W41CA   CA33    W41S    SN34
        PENCK   HI34    W33SA   SA35
        W32T    TS33    W32SA   SA34

        W32K    KC34    W32H    HI35
        W32S    SN33    W31CA   CA32
        W31T    TS32    W31S    SN32
        W31K    KC33    W31SA   SA33
        W22SA   SA32    W22H    HI33
        W21CA   CA31    W21T    TS31
        W21SA   SA31    W21S    SN31
        W21K    KC32    W21H    HI32
        W11K    KC31    W11H    HI31

        Sweets%20pure   ST29
        G'zOne%20TYPE-R CA28
        Sweets  ST26    talby   ST25
        A5520SA ST2A    A5518SA ST28
        INFOBAR ST22    A5517T  TS2C
        A5516T  TS2B    A5515K  KC27
        A5514SA ST27    A5512CA CA27
        A5511T  TS2A    A5509T  TS29
        A5507SA ST24    A5506T  TS28
        A5505SA SA27    A5504T  TS27

        A5503SA     SA26        A5502K      KC24/KC25
        A5501T      TS26        A5407CA     CA26
        A5406CA     CA25        A5405SA     ST23
        A5404S      SN25        A5403CA     CA24
        A5402S      SN24        A5401CA-II  CA23
        A5401CA     CA23        A5306ST     ST21
        A5305K      KC22        A5304T      TS24
        A5303H-II   HI24        A5303H      HI23
        A5302CA     CA22        A5301T      TS23
        C5001T      TS21

        A1405PT     PT21
        A1404S      SN29        A1403K      KC26
        A1402S-II   SN27        A1402S-II-NC SN28
        A1402S      SN26        A1401K      KC23
        A1305SA     SA28        A1304T-II   TS25
        A1304T      TS25        A1303SA     SA25
        A1302SA     SA24        A1301S      SN23
        A1101S      SN22

        A3015SA     SA22        A3014S      SN21
        A3013T      TS22        A3012CA     CA21
        A3011SA     SA21        C3003P      MA21
        C3002K      KC21        C3001H      HI21

        A1014ST     ST14        A1013K      KC15
        A1012K      KC14        A1011ST     ST13
        C1002S      SN17        C1001SA     SY15
        C452CA      CA14        C451H       HI14
        C415T       TS14        C414K       KC13
        C413S       SN15/SN16   C412SA      SY14
        C411ST      ST12        C410T       TS13
        C409CA      CA13        C408P       MA13
        C407H       HI13        C406S       SN13
        C405SA      SY13        C404S       SN12/SN14
        C403ST      ST11        C402DE      DN11
        C401SA      SY12        C313K       KC12
        C311CA      CA12        C310T       TS12
        C309H       HI12        C308P       MA11/MA12
        C307K       KC11        C305S       SN11
        C304SA      SY11        C303CA      CA11
        C302H       HI11        C301T       TS11
        C202DE      DN01        C201H       HI01/HI02

        TT51    TST9        TK41    KCU1
        TS41    SYT5        TK40    KCTD
        TT32    TST8        TT31    TST7
        TK31    KCTC        TS31    SYT4
        TK23    KCTB        TK22    KCTA
        TT22    TST6        TK21    KCT9
        TT21    TST5        TT11    TST4
        TK12    KCT8        TS11    SYT3
        TK11    KCT7        TD11    MIT1
        TP11    MAT3        TK05    KCT6
        TT03    TST3        TK04    KCT5
        TK03    KCT4        TS02    SYT2
        TP01    MAT1/MAT2   TT02    TST2
        TK02    KCT2/KCT3   TK01    KCT1
        TT01    TST1        TS01    SYT1

        D301SA      SYC1        D302T/701G  TSC1/TSI1
        D303K/702G  KCC1/KCI1   D304K/703G  KCC2/KCI2
        D306S/705G  SNC1/SNI1   D305P/704G  MAI1/MAC1/MAI2/MAC2
    )};
    # SNC1/SNI1 �� SNC1 �� SNI1 ��ʬ�򤹤�
    foreach my $key ( keys %$EZWEB_NAME ) {
        next unless ( $key =~ m#/# );
        foreach my $sub ( split( "/", $key ) ) {
            $EZWEB_NAME->{$sub} = $EZWEB_NAME->{$key};
        }
    }
    # ���� .mmf �б�����ʼ�ưȽ�̤˼��Ԥ��뵡���
    my $EZWEB_MMF_OK = [qw(
        C313K TK11 TK03
    )];
    # au��TU-KA �ϰ��Ҽ�ưȽ��
    my $EZWEB_AREA_MAP = {qw(
        05      au_kanto_chubu
        0700    au_kansai
        0701    au_kyushu
        0702    au_chugoku
        0703    au_tohoku
        0704    au_hokuriku
        0705    au_hokkaido
        0706    au_shikoku
        0707    au_okinawa
        0800    tuka_tokyo
        0801    tuka_kansai
        0802    tuka_tokai
    )};
# -------------------------------------------------------------------- #
#   ASTEL dot.I ������δ��ξ����depth��
# -------------------------------------------------------------------- #
    my $ASTEL_DEPTH = {qw(
        AJ-51   2
    )};                                 # ���老�Ȥ� depth
# -------------------------------------------------------------------- #
#   DDI �ݥ��å� P�᡼��DX ���������depth��
# -------------------------------------------------------------------- #
    my $PDX_DEPTH = {
        "G2"   =>  1,
        "C4"   =>  2,
        "C256" =>  8,
        "CF"   => 16,
    };                                  # �������󤴤Ȥ� depth �Ѵ�
# -------------------------------------------------------------------- #
sub phone_info {

#   �֥饦��̾��J-PHONE ���̡�ezWeb ���̴Ķ��ѿ�
    my $agent  = $ENV{HTTP_USER_AGENT};
    my $accept = $ENV{HTTP_ACCEPT};

#   �֥饦��������Ǽ����ϥå���
    my $phone = {};
    $phone->{agent} = $agent;

#   �ե����륿�����б�����

    $phone->{image_jpeg} ++ if ( $accept =~ m#image/jpeg# );        # JPEG
    $phone->{image_png}  ++ if ( $accept =~ m#image/png# );         # PNG
    $phone->{image_gif}  ++ if ( $accept =~ m#image/gif# );         # GIF
    $phone->{image_bmp}  ++ if ( $accept =~ m#image/bmp# );         # BMP
#   $phone->{movie_noa}  ++;                                        # Nancy
    $phone->{audio_mmf}  ++ if ( $accept =~ m#application/x-smaf# );# .mmf
    $phone->{audio_pmd}  ++ if ( $accept =~ m#application/x-pmd# ); # .pmd
    $phone->{audio_smd}  ++ if ( $accept =~ m#audio/x-smd# );       # .smd .smz
    $phone->{text_html} ++;                                         # .html
    $phone->{text_hdml} ++ if ( $accept =~ m#\Whdml# );             # .hdml

# ��Vodafone 3G���Ӥ� HTTP_USER_AGENT
#   Vodafone/1.0/V702NK/NKJ001 Series60/2.6 Nokia6630/2.39.148 Profile/MID ...
#   Vodafone/1.0/V802SE/SEJ001 Browser/SEMC-Browser/4.1 Profile/MIDP-2.0 ...
#   Vodafone/1.0/V802SH/SHJ001 Browser/UP.Browser/7.0.2.1 Profile/MIDP-2.0 ...
#   Vodafone/1.0/V902SH/SHJ001 Browser/UP.Browser/7.0.2.1 Profile/MIDP-2.0 ...
#   MOT-V980/80.2F.2E. MIB/2.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1
# ��Vodafone 3G���ӤΥ롼�ȥɥ������(HTML�ե�����)����������
#   V702MO��V702sMO 10 Kbytes
#   V802N           21103 bytes
#   V902SH��V802SH  22 kbytes
#   V802SE          30kbytes
# ���������������ե������ޤ᤿�ڡ������Τ����̤�300KB��OK
#   http://www.sharp-mobile.com/UAProf/V802SH_J001_3g.xml
#   http://www.sharp-mobile.com/UAProf/V902SH_J001_3g.xml
#   <prf:WmlDeckSize>49152</prf:WmlDeckSize>
#   <vfx:FlashDownloadMaxSize>102400</vfx:FlashDownloadMaxSize>
#   <mms:MmsMaxMessageSize>307200</mms:MmsMaxMessageSize>

    if ( $agent =~ m#^(J-PHONE|Vodafone|J-EMULATOR|Vemulator)/#i || $ENV{HTTP_X_JPHONE_MSNAME} ) {
        my( $carrier, $ver, $name ) = split( "/", $agent );
        $ver = undef unless ( $ver =~ /[0-9\.]/ );          # �Х�����
        $name = $ENV{HTTP_X_JPHONE_MSNAME} if $ENV{HTTP_X_JPHONE_MSNAME};

        $phone->{type}   = "jphone";
        $phone->{ver}    = $ver;
        $phone->{code}   = $name;       # J-DN03_a
        $name =~ s/ .*$//;              # J-SH51 SH�ʥ᡼����̾�����
        $name =~ s/_[a-z]$//;           # J-DN03�����������
        $phone->{name}   = $name;       #
        $phone->{uid}    = &get_phone_uid_jphone();         # UID ���������

        my $jsize  = $ENV{HTTP_X_JPHONE_DISPLAY};
        my( $width, $height ) = split( /\*/, $jsize );

        my $jcolor = $ENV{HTTP_X_JPHONE_COLOR};
        $phone->{color}  = ( $jcolor =~ /^C/i );
        if ( $jcolor =~ /(\d+)$/ ){
            my $num   = $1;
            my $depth = 1;
            while ( $num > 2 ** $depth ) {
                $depth ++;
            }
            $phone->{depth} = $depth;
        }
        $phone->{width}  = $width;
        $phone->{height} = $height;

        if ( $carrier eq "J-PHONE" ) {
            $phone->{vodafone_2g} ++;           # Vodafone 2G��2.5G����
            if ( $ver < 3.0 ) {                 # ���ơ���������б�����
                $phone->{disable_post} ++;      # POST�ػߡ�GET�Τ�
            } else {                            # ���ơ�������б�����
                $phone->{image_jpeg} ++;        # JPEG�б�
            }
            if ( $ver < 4.0 ) {                 # �ѥ��å����б�����
                $phone->{cache} = 6000;         # 6KB����å���
            } else {                            # �ѥ��å��б�����
                $phone->{cache} = 12000;        # 12KB����å���
            }
        } else {
            $phone->{vodafone_3g} ++;           # Vodafone 3G����
            $phone->{cache} = 307200;           # 300KB����å���(������ޤ�)
        }

        $phone->{image_png}  ++;                            # ɬ��PNG�б�
        $phone->{audio_mmf} ||= $ENV{HTTP_X_JPHONE_SMAF};   # 16�²���
        $phone->{audio_mmf} ||= $ENV{HTTP_X_JPHONE_SOUND};  # 4�²���
        $phone->{sound}  = (split( /,/, $ENV{HTTP_X_JPHONE_SMAF} ))[0]; #�²���
        $phone->{java}   = $ENV{HTTP_X_JPHONE_JAVA};        # Java �б�

        # XHTML�б�
        # ư���б�
        if( $phone->{vodafone_3g} || ( $phone->{name} =~ m/^V80\d/ ) ) {      # 3G��V8(W��)
            $phone->{xhtml_native}++;
            $phone->{movie_mp4}++;
            $phone->{movie_ok}++;
            $phone->{voice_ok}++;
            $phone->{movie_qcif}++;
            $phone->{movie_sub_qcif}++;
        } else {
            $phone->{html_native}++;
        }

    } elsif ( $agent =~ m#^((KDDI-)?[A-Z]+[A-Z0-9]+\s+)?UP\.Browser/#i ) {
        # au / TU-KA

        my $ecolor = $ENV{HTTP_X_UP_DEVCAP_ISCOLOR};
        my $edepth = $ENV{HTTP_X_UP_DEVCAP_SCREENDEPTH};
        my $esize  = $ENV{HTTP_X_UP_DEVCAP_SCREENPIXELS};
        my $ezweb  = $ENV{HTTP_X_UP_SUBNO};
        my( $width, $height ) = split( ",", $esize );

        # KDDI-HI21 UP. Browser/6.0.2.254(GUI) MMP/1.1 �� C3001H
        # UP. Browser/3.01-HI02 UP.Link/3.2.1.2        �� A1000

        # �ǽ�� / �θ��˥С�������ֹ椬���
        my $ver  = ( $agent =~ m#^[^\/]+\/([\d\.]+)#i )[0];
        # �ǽ�� - �θ��˵���̾�����
        my $name = ( $agent =~ m#^[^\-]+\-([A-Z]\w+)#i )[0];

        # ����̾�� %20 ������С�Ⱦ�ѥ��ڡ������Ѵ�����
        my $prodname = $EZWEB_NAME->{$name};
        $prodname =~ s/%20/ /g;

        $phone->{type}   = "ezweb";
        $phone->{name}   = $prodname || "($name)";
        $phone->{code}   = $name;
        $phone->{color}  = ( $ecolor > 0 );
        $phone->{width}  = $width;
        $phone->{height} = $height;
        $phone->{depth}  = ( $edepth =~ /^(\d+)/ )[0];  #��16,RGB565��
        $phone->{ver}    = $ver;
        $phone->{uid}    = &get_phone_uid_ezweb();  # UID ���������
        $phone->{image_bmp} ++;                     # ɬ��BMP
        $phone->{image_png} = ( $ecolor > 0 );      # ���顼�����PNG
        $phone->{text_html} = ( $accept =~ m#text/html# );
        $phone->{text_hdml} ++;

        # (GUI) �ȴޤൡ��� XHTML �ͥ��ƥ��ֵ����2002/11/04��
        if ( $agent =~ /\(GUI\)/ ) {
            $phone->{xhtml_native} ++;
        } else {
            $phone->{hdml_native} ++;
        }

        # .mmf �б��ϴ���Ū�˼�ưȽ�̤Ǥ��뤬����������ϼ�ưȽ�̤Ǥ��ʤ�
        my $mmf_ok = { map {$_=>1} @$EZWEB_MMF_OK };
        $phone->{audio_mmf} ++ if $mmf_ok->{$phone->{name}};
        $phone->{audio_qcp} ++ if ( $accept =~ m#audio/vnd.qcelp# );

        $phone->{image_gif} ++;                     # �Ƕ��GIF�⼫ư�б�
        my $max_pdu = $ENV{HTTP_X_UP_DEVCAP_MAX_PDU};
        $phone->{cache} = $max_pdu if $max_pdu;

        # �ţ����������������¤��ä˸���������(HDML/BMP)
        $phone->{ezweb_mono} ++ if ( $max_pdu && $max_pdu < 1500 );

        # au��TU-KA �ϰ��Ҽ�ưȽ��
        my $ezregex = join( "|", sort keys %$EZWEB_AREA_MAP );
        if ( $phone->{uid} =~ /^($ezregex)/ ) {
            $phone->{ezweb_area} = $EZWEB_AREA_MAP->{$1};
        }

        # EZ�ࡼ�ӡ�
        # ��Ƭ�ΰ�夬�б�������ɽ���Ƥ���
        my $ezmovie = ( $ENV{HTTP_X_UP_DEVCAP_MULTIMEDIA} =~ m/^(\d)/ )[0];
        # �������¤Τ��뵡�A1302SA�ḫ���ʤ��Ȥߤʤ�
        $ezmovie = 0 if( $ezmovie == 4 );
        # ���б��ʤ�0�����äƤ���
        $phone->{ezmovie} = $ezmovie;

        # .amc�б�
        $phone->{movie_amc}++ if( $ezmovie >= 1 && $ezmovie <= 6 );
        # .3g2�б�
        $phone->{movie_3g2}++ if( $ezmovie >= 5 );

        # ư���б�
        $phone->{movie_ok}++ if( $phone->{ezmovie} );
        $phone->{voice_ok}++ if( $phone->{ezmovie} );
        # ư�襵����
        $phone->{movie_qcif}++     if( $phone->{ezmovie} =~ m/^[156789]$/ );   # QCIF
        $phone->{movie_sub_qcif}++ if( $phone->{ezmovie} =~ m/^[1356789]$/ );  # sub-QCIF
        $phone->{movie_light}++    if( $phone->{ezmovie} =~ m/^[12356789]$/ ); # light
        $phone->{movie_240x180}++  if( $phone->{ezmovie} =~ m/^[9]$/ );        # 240x180
        $phone->{movie_qvga}++     if( $phone->{ezmovie} =~ m/^[9]$/ );        # QVGA

    } elsif ( $agent =~ m#^DoCoMo/#i ) {                # DoCoMo

        # DoCoMo/1.0/SO503i/c10
        # DoCoMo/2.0 P2101V (c100)
        my( $docomo, $ver, $name, $sub ) = split( /[\/\s\(\)]+/, $agent );

        my $imode_depth = {
            ( map { $_ => 1 } @$DOCOMO_BLACK ),         # �������Ĵ
            ( map { $_ => 2 } @$DOCOMO_GLAY  ),         # ���졼����Ĵ(����)
        };
        my $depth = $imode_depth->{$name};              # 2001/04/05
        $depth ||= $DOCOMO_DEFAULT_DEPTH;               # 2000/07/19

        $phone->{type}   = "docomo";
        $phone->{code}   = $name;
        $phone->{name}   = $name;
        $phone->{color}  = ( $depth >= 8 );
        $phone->{depth}  = $depth;
        $phone->{ver}    = $ver;

        $phone->{sub}    = $sub;
        $phone->{uid} = &get_phone_uid_docomo();        # UID ���������
        $phone->{image_gif}  ++;                        # ɬ��GIF

        my $no_mld = { map {$_=>1} @$DOCOMO_NO_MLD };   # �忮���ǥ�
        $phone->{audio_mld} ++ unless $no_mld->{$name}; # ����Ū���б�

        my $no_voice = { map {$_=>1} @$DOCOMO_NO_VOICE };   # ��ܥ���
        $phone->{docomo_voice} ++ unless $no_voice->{$name};

        my $cache = ( $sub =~ /(?:^|[^A-Za-z])c(\d+)/ )[0] * 1024;
        $phone->{cache} = $cache if $cache;
        if ( $name =~ /^[A-Z]+(50[5-9]|70[0-9]|90[0-9]|880|851)i/ ){
            $phone->{qvga} ++;                          # QVGA
        }

        # DoCoMo FOMA/PDC/PHS �ζ���

        if ( $name =~ /^[A-Z]+(\d{4}|9\d\di|7\d\di|880i|851i)/ ) {
            $phone->{docomo_foma} ++;                   # FOMA
        } elsif ( $name =~ /^[A-Z]+\d{3}[iI]/ ) {
            $phone->{docomo_pdc} ++;                    # PDC
        } elsif ( $name =~ /^\d{3}/ ) {
            $phone->{docomo_phs} ++;                    # PHS

        }

        # DoCoMo JPEG �б������Ƚ�̡�2003/10/23��

        if ( $phone->{docomo_foma} ) {
            # FOMA �������� JPEG �б�
            $phone->{image_jpeg} ++;
        } elsif ( $phone->{docomo_pdc} ) {
            # PDC �����굡�������� JPEG �б�
            my $nojpeg_map = { map {$_=>1} @$DOCOMO_NO_JPEG };
            $phone->{image_jpeg} ++ unless $nojpeg_map->{$name};
        }

        # i�⡼���б�HTML�С������

        my $ihtml1 = { map {$_=>"1.0"} @$DOCOMO_HTML1 };
        my $ihtml2 = { map {$_=>"2.0"} @$DOCOMO_HTML2 };
        my $ihtml3 = { map {$_=>"3.0"} @$DOCOMO_HTML3 };
        my $ihtml4 = { map {$_=>"4.0"} @$DOCOMO_HTML4 };
        my $ihtmlv = $ihtml4->{$name} || $ihtml3->{$name} ||
                     $ihtml2->{$name} || $ihtml1->{$name};
        if( !$ihtmlv ) {
            if( $phone->{docomo_foma} ||
               ($name =~ m/^[a-zA-Z]+(50[5-9]|70[0-9]|90[0-9])/) ) {
                $ihtmlv = "5.0";
            }
        }
        $phone->{docomo_ihtmlv} = $ihtmlv;

        # i�⡼�ɳ�ʸ��
        # docomo_std_emoji�����ʤ顢��ĥ��ʸ�������Ƚ��Ǥ���

        if ( $ihtmlv && $ihtmlv < 4.0 ) {
            $phone->{docomo_std_emoji} ++;  # ɸ�೨ʸ������
        }

        # �ǥ����ץ쥤��������Ĵ�٤�
        if( $DOCOMO_DISPLAY->{$phone->{name}} =~ m/^(.+?)x(.+?)$/ ) {
            $phone->{width}  = $1;
            $phone->{height} = $2;
        }

        # i�⡼�ɥ���ߥ졼��7.0�ϡ�16�ɥåȥե�������ѤȤߤʤ�
        if ( $phone->{name} eq "ISIM70" &&
             ! defined $phone->{width} &&
             $sub =~ /(?:^|\W)W(\d+)H(\d+)(?:\W|$)/ ) {
            my( $width, $height ) = ( $1, $2 );
            if ( $width <= 30 && $height <= 20 ) {
                $phone->{width}  = $1 *  8;
                $phone->{height} = $2 * 16;
            }
        }

        # XHTML�б�
        if( $phone->{docomo_foma} ) {
            my $no_xhtml = { map {$_=>1} @$DOCOMO_NO_XHTML };       # FOMA�Τ���XHMTL���б��Τ��
            $phone->{xhtml_native}++ unless( $no_xhtml->{$name} );  # FOMA�ϴ���Ū���б�
        }

        # i�⡼�����
        if( $phone->{docomo_foma} ) {
            # mp4
            my $no_mp4 = { map {$_=>1} @$DOCOMO_NO_MP4 };   # FOMA�Τ���MP4���б��Τ��
            unless( $no_mp4->{$name} ) {                    # FOMA�ϴ���Ū���б�
                $phone->{movie_ok}++;
                $phone->{voice_ok}++;
                $phone->{movie_mp4}++;
                $phone->{movie_qcif}++;
                $phone->{movie_sub_qcif}++;
            }
            # asf
            my $asf = { map {$_=>1} @$DOCOMO_ASF };         # FOMA�Τ���ASF�б��Τ��
            if( $asf->{$name} ) {
                # $phone->{movie_ok}++;                     # 15�ä��������Ǥ��ʤ��餷���Τ����б��Ȥ��Ƥ���
                $phone->{voice_ok}++;
                $phone->{movie_asf}++;
                $phone->{movie_sub_qcif}++;
            }
        }

    } elsif ( $agent =~ m#^ASTEL/#i ) {                 # Astel

        # ASTEL/1.0/J-0511.00/c10/smel
        my( $docomo, $ver, $name, $sub ) = split( "/", $agent, 4 );

        my( $maker, $code ) = ( $name =~ /(\D+)(\d\d\d)/ );
        my $sname = sprintf( "A%s%d", $maker, $code ) if $code;
        my $depth = $ASTEL_DEPTH->{$sname};

        $phone->{type}   = "astel";
        $phone->{code}   = $name;
        $phone->{name}   = $sname || "($name)";
        $phone->{color}  = ( $depth >= 8 );
        $phone->{depth}  = $depth;
        $phone->{ver}    = $ver;
        $phone->{sub}    = $sub;
        $phone->{image_gif} ++;                 # ɬ��GIF
        $phone->{image_png} ++;                 # ɬ��PNG
        $phone->{cache} = ( $sub =~ /(?:^|[^A-Za-z])c(\d+)/ )[0] * 1024;

    } elsif ( $agent =~ m#^Mozilla/\d+.\d+\(DDIPOCKET;(.*?)\)#i ) {

        # Mozilla/3.0(DDIPOCKET;JRC/AH-J3001V,AH-J3002V/1.0/0100/c50)CNF/2.0
        my $ddip = $1;                          # AirH" Phone
        my( $maker, $name, $ver, $sub, $cache ) = split( "/", $ddip );
        $phone->{type}  = "ahphone";
        $phone->{code}  = $name;
        $phone->{name}  = $name;
        $phone->{ver}   = $ver;
        $phone->{sub}   = $sub;
        $phone->{image_gif} ++;                 # ɬ��GIF
        $phone->{cache} = ( $cache =~ /(?:^|[^A-Za-z])c(\d+)/ )[0] * 1024;

    } elsif ( $agent =~ m#^L-mode/#i ) {                # L-mode

        # L-mode//1.0/AT/SHAUX-W71/10240/1000
        # L-mode//1.0/AT/NTTxxxxxxxxxxxxx-000/10240/1000
        $phone->{type}   = "lmode";
        $phone->{ver} = ( $agent =~ m#//(\d+\.\d+)/# )[0];
        $phone->{image_gif} ++;                 # ɬ��GIF

    } elsif ( $agent =~ m#^PDXGW/#i ){                    # DDIP

        my( $ver  ) = ( $agent =~ m#^PDXGW/([\d\.]+)# );
        my( $stat ) = ( $agent =~ m#\((.*)\)# );
        $stat ||= "TX=6;TY=3;GX=72;GY=36;C=G2;G=B2;GI=0";
        my $hash = {};
        foreach my $elem ( split( ";", $stat ) ){
            my( $key, $val ) = split( "=", $elem );
            $key =~ tr#a-z#A-Z#;
            $key =~ s#^\s+##;
            $key =~ s#\s+$##;
            $val =~ s#^\s+##;
            $val =~ s#\s+$##;
            $hash->{$key} = $val;
        }

        $phone->{type}   = "pdx";
        $phone->{ver}    = $ver;
        $phone->{color}  = ( $hash->{C} =~ /^C/ );
        $phone->{depth}  = $PDX_DEPTH->{$hash->{C}};
        $phone->{width}  = $hash->{GX};
        $phone->{height} = $hash->{GY};
        $phone->{info}   = $hash;

    } else {                                        # Other (PC)

        $phone->{type}   = undef;                   # ������̤���
        $phone->{color}  = ! undef;                 # �Ǥ⥫�顼���ʡ�

    }

    if ( $phone->{width} >= 220 ) {
        $phone->{qvga} ++;                          # QVGA
    }

    if ( ! $phone->{width} && $phone->{qvga} ) {
        $phone->{width} = 240;                      # QVGA 2004/12/01
    }

    if ( $phone->{type} ) {
        $phone->{"type_".$phone->{type}} ++;        # ���󥿥�Ƚ��
    }

    # �ϥå���ؤλ��Ȥ��֤�
    $phone;
}
# -------------------------------------------------------------------- #
#   UID ����Ф�
#   ��������UID�η������å��ΤߤǤϺ��β�ǽ�Τ��ᡢ
#   ��̩�ˤϣǣץ��󥿣ɣХ��ɥ쥹�����¤Ȥ���ɬ��
# -------------------------------------------------------------------- #
sub get_phone_uid_docomo {
    # ��⡼�ɤξ��ϡ��������ѿ� uid �� 2��ο����ǻϤޤ�
    # 00 (PDC) �ޤ��� 01 (FOMA) ��ɽ��
    # �͸��������Ȥ� uid=NULLGWDOCOMO ������Τ߼�����ǽ
    # ��phone.pl �μ����ǤϤ���� GET �������Τ߼�����ǽ
    # ��POST �������ϼ����Ǥ��ʤ��ʥ�������ɤ�ʤ������
    my $phone_uid = ( $ENV{QUERY_STRING} =~ /(?:^|&)uid=([%\w]+)(?:&|$)/ )[0];
    $phone_uid = undef unless ( $phone_uid =~ /^\d\d\w+$/ );
    $phone_uid;
}
sub get_phone_uid_jphone {
    # �ʥե���ξ��ϡ��Ķ��ѿ� HTTP_X_JPHONE_UID �򻲾Ȥ���
    # �գɣ�����̤�����ξ��ϡ�NULL ���Ϥ����⤷��ʤ�
    # ��uid=1&pid=XXX&sid=XXX ������Τ߼�����ǽ
    my $phone_uid = $ENV{HTTP_X_JPHONE_UID};
    $phone_uid = undef if ( $phone_uid eq "NULL" );
    $phone_uid;
}
sub get_phone_uid_ezweb {
    # �ţڥ����֤ξ��ϡ�4��ʾ�ο����ǻϤޤꡢ
    # ɬ�� ezweb.ne.jp �� ido.ne.jp �ǽ����
    # ������������ȤǤ������ǽ
    my $phone_uid = $ENV{HTTP_X_UP_SUBNO};
    $phone_uid = undef unless ( $phone_uid =~ /^\d{4}.*(ezweb|ido)\.ne\.jp$/i );
    $phone_uid;
}
# -------------------------------------------------------------------- #
;1;
# -------------------------------------------------------------------- #
