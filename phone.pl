# -------------------------------------------------------------------- #
#   phone.pl - 携帯電話からの環境変数を解析し、ハッシュへの参照を返す
# -------------------------------------------------------------------- #
=head1 NAME

phone.pl - 携帯電話からの環境変数を解析し、ハッシュへの参照を返す

=head1 SYNOPSIS

【携帯キャリアを判別した Location 飛ばし】

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

携帯電話からのアクセスを受け付けるCGI向けに、携帯電話に関する環境変数を
解析して、使いやすい形のハッシュを作成し、その参照を返します。
ここでは、以下の手順でハッシュを取得するものとします。

    require "phone.pl";
    my $phone = &phone_info();

携帯電話会社の判別には、type プロパティを利用します。

    $phone->{type}  ⇒  携帯電話会社（キャリア）

携帯3キャリアの type プロパティの値は以下のようになります。

        "docomo"    ⇒  NTTドコモiモード（PHSブラウザフォンを含む）
        "jphone"    ⇒  ボーダフォン
        "ezweb"     ⇒  au・TU-KA EZweb

過去の phone.pl との互換のため、ボーダフォンは "jphone" と判別します。
これら携帯3キャリアの他に、PHS や L モードも判定します。

        "astel"     ⇒  ASTEL dotI
        "ahphone"   ⇒  AirH" Phone
        "pdx"       ⇒  PメールDX
        "lmode"     ⇒  NTT Lモード
        ""          ⇒  PC（値は空です）

type プロパティ以外に参照できる値は、以下の通りです。

    ＜端末情報系＞
    $phone->{name}          ⇒  携帯機種名（商品名など）
    $phone->{code}          ⇒  携帯機種名（製品コードなど）
    $phone->{color}         ⇒  カラー表示対応（カラー＝真、白黒＝偽）
    $phone->{ver}           ⇒  バージョン情報
    $phone->{cache}         ⇒  キャッシュ容量（バイト単位）
    $phone->{qvga}          ⇒  QVGA液晶搭載機種（QVGA＝真）
    $phone->{width}         ⇒  ディスプレイサイズ横幅（ピクセル単位）
    $phone->{height}        ⇒  ディスプレイサイズ縦幅（ピクセル単位）

以下のプロパティは、対応機種であれば真となります。（ezmovieを除く）

    ＜画像表示系＞
    $phone->{image_jpeg}    ⇒  JPEG画像
    $phone->{image_png}     ⇒  PNG画像
    $phone->{image_gif}     ⇒  GIF画像
    $phone->{image_bmp}     ⇒  BMP画像

    ＜音声再生系＞
    $phone->{audio_mmf}     ⇒  着メロ .mmf (SMAF)
    $phone->{audio_pmd}     ⇒  着メロ .pmd
    $phone->{audio_smd}     ⇒  着メロ .smd
    $phone->{audio_mld}     ⇒  着メロ .mld
    $phone->{audio_qcp}     ⇒  着ボイス .qcp (EZ)

    ＜動画再生系＞
    $phone->{movie_amc}     ⇒  EZムービー AMC(.amc)
    $phone->{movie_3g2}     ⇒  EZムービー 3GPP2(.3g2)

    ＜NTTドコモiモード専用＞
    $phone->{docomo_foma}   ⇒  NTTドコモFOMA端末
    $phone->{docomo_pdc}    ⇒  NTTドコモPDC端末
    $phone->{docomo_phs}    ⇒  NTTドコモPHS端末

    ＜ボーダフォン専用＞
    $phone->{vodafone_2g}   ⇒  ボーダフォンPDC端末
    $phone->{vodafone_3g}   ⇒  ボーダフォン3G端末
    $phone->{disable_post}  ⇒  method="post" 使用不可

    ＜EZウェブ専用＞
    $phone->{ezweb_mono}    ⇒  EZウェブ白黒HDML端末（au 300系。1.4KB）
    $phone->{hdml_native}   ⇒  EZウェブHDML端末（au 300〜10xx系）
    $phone->{xhtml_native}  ⇒  EZウェブXHTML端末（au 110x系〜、WIN）
    $phone->{ezmovie}       ⇒  EZムービー対応状況（0〜9）

機種によっては、ディスプレイサイズやキャッシュ容量などを正確に
取得できない場合もあります。（その場合は値は偽となります）
また、制限がありますが UID（携帯端末固有記号）を取得できます。

    $phone->{uid}           ⇒  UID（携帯端末固有記号）

ただし、ｉモード機では公式サイトのドメイン下でのみ取得可能、
ボーダフォン機では、公式サイトの pid・sid 利用時のみ取得可能、
ＥＺウェブ機種では、公式／勝手サイト問わず取得可能です。
なお、ＵＩＤは詐称可能のため、より厳密に固体判別を行うためには
ＧＷセンタＩＰアドレスによるアクセス制限の併用が必要です。

=head1 COMMENT

phone.pl はご自由にお使いください。
ご意見・バグ情報などお待ちしております。

=head1 VERSIONS

    Version 1.01 (2000/05/11) 最初のバージョン
    Version 1.02 (2000/05/12) ezWeb 商品名変換対応、DoCoMo バグフィックス
    Version 1.03 (2001/02/19) DoCoMo 機種名は i まで付ける
    Version 1.04 (2001/04/05) DoCoMo 最新機種対応、アステル対応
    Version 1.10 (2002/03/25) au 最新機種対応、ファイルタイプ実験対応
    Version 1.11 (2002/04/26) DoCoMo 着メロ機種判別対応
    Version 1.12 (2002/05/07) DoCoMo FOMA、au 新機種、TK11・C313K 着メロ対応
    Version 1.13 (2002/09/30) au 新機種、audio/vnd.qcelp 着メロ対応
    Version 1.14 (2002/10/08) au 自動判別方式改良
    Version 1.15 (2002/11/04) au 新機種対応（SA22→A3015SA）
    Version 1.17 (2002/11/27) au 新機種対応（A5303H／A5302CA／TT22）
    Version 1.18 (2002/11/28) hdml_native/xhtml_native/disable_post
    Version 1.19 (2002/11/28) hdml_native/xhtml_native 修正
    Version 1.20 (2002/12/06) au 新機種対応（A1101S/TK21/TK22）、TK03 はMMF対応
    Version 1.21 (2003/04/16) au 新機種対応（A1301S/A1302SA/TK31/TS31）
    Version 1.22 (2003/04/17) au 新機種対応（TK23/A5402ST）。A5402ST は推測
    Version 1.30 (2003/05/02) uid 取得可能（制限あり）
    Version 1.32 (2003/06/10) DDI Pocket AirH" Phone対応（AH-J3001V/AH-J3002V）
                              au 新機種対応（A5402S/A5401CA/A5306ST/A5305K）
                              （A5402ST は誤りで、正しくは A5306ST でした）
    Version 1.33 (2003/07/01) DOCOMO_GLAY バグ修正(今頃?)
    Version 1.34 (2003/08/01) au 新機種対応（A5303H-II/A1304T/TT31）
    Version 1.35 (2003/08/17) au 新機種対応（A1401K/A1303SA）
                              au 小容量白黒機種自動判別追加（ezweb_mono）
                              au 地域会社自動判別追加 (ezweb_area)
                              DoCoMo (docomo_foma docomo_pdc docomo_phs)追加
    Version 1.36 (2003/09/17) au 新機種対応 (A5307ST/A5501T/W11H)
    Version 1.37 (2003/10/23) DoCoMo JPEG 判別対応（image_jpeg）
                              au 機種名変更（A5307ST⇒INFOBAR）
    Version 1.38 (2003/10/26) DoCoMo 着ボイス非対応機種判別(docomo_voice)
    Version 1.39 (2004/02/06) DoCoMo 900i シリーズ対応
    Version 1.40 (2004/02/13) au/TU-KA 新機種対応（W11K他）
    Version 1.41 (2004/03/08) DoCoMo 拡張絵文字非対応機種判別(docomo_std_emoji)
    Version 1.42 (2004/03/16) au/TU-KA 新機種対応（A5405SA他）
    Version 1.43 (2004/06/29) DoCoMo ディスプレイサイズ判別追加
                              (3キャリア全て取得可能:width:height)
                              au/TU-KA 新機種対応（A5506T他）
    Version 1.44 (2004/07/26) DoCoMo QVGA 新機種対応（F880iES他）
    Version 1.45 (2004/09/17) DOCOMO_QVGA 更新
    Version 1.46 (2004/09/28) au/TU-KA 新機種対応（A5504T、A1305SA他）
    Version 1.47 (2004/10/19) iモードHTMLシミュレータIIもQVGA対応
    Version 1.48 (2004/11/09) EZムービー ezmovie、movie_amc、movie_3g2
    Version 1.49 (2004/12/01) QVGA機種の横幅は240ピクセル、EZ新機種対応
    Version 1.50 (2004/12/22) iモードHTMLシミュレータ7.0は16ビットフォント換算
    Version 1.51 (2005/01/05) ドコモ700iシリーズ対応
    Version 1.52 (2005/01/17) Vodafone キャッシュ容量判定変更、W21CA対応
    Version 1.53 (2005/01/26) Vodafone V902SH他、新3G携帯対応
    Version 1.54 (2005/01/26) Vodafone 702MO 対応（MOT-V980）
    Version 1.55 (2005/01/31) Vodafone バージョン番号判定バグ修正
    Version 1.56 (2005/02/02) Vodafone 3G携帯は 300KBキャッシュとみなす
    Version 1.57 (2005/02/18) au 新機種対応（W31SA）
    Version 1.58 (2005/03/22) au/TU-KA 新機種対応（PENCK/TT51）
    Version 1.59 (2005/03/28) au 新機種対応（W31K/W31S）
    Version 1.60 (2005/03/30) au 判別バグ修正（W31K/W31S）、POD更新
    Version 1.61 (2005/06/04) au 新機種対応（Sweets）
    Version 1.62 (2005/06/18) 動画対応機種判別（Thanks to MIZUNOTOMOAKI）
    Version 1.63 (2005/06/20) movie_3g2 判別条件修正
    Version 1.64 (2005/09/03) SO213iS 判別修正、SH851i 対応、au 新機種対応
    Version 1.65 (2005/09/27) au 新機種対応（Thanks to IIJIMA）
    Version 1.66 (2006/02/21) au 新機種対応（W41K/Sweets pure他）

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
#   NTT DoCoMo i-mode 機種毎の既知情報（depth）
#   i-mode は基本的に機種名・キャッシュ容量以外の環境変数が入りません
#   そのため必要な情報は自前で保持する必要があります（不便だなぁ）
# -------------------------------------------------------------------- #
    my $DOCOMO_DEFAULT_DEPTH = 8;       # 標準の depth
    # 白黒２階調機種
    my $DOCOMO_BLACK = [qw(
        D501i       ER209i      F501i       N501i
        NM502i      R209i       P501i
    )];
    # 白黒４階調機種
    my $DOCOMO_GLAY = [qw(
        N209i       N502i       N821i       P209i
        P502i       P821i       R691i       SO502i
    )];
    # 着信メロディ .mld 非対応機種（NM502iは容量制限が非常に厳しい）
    my $DOCOMO_NO_MLD = [qw(
        D501i       F501i       N501i       P501i       NM502i
    )];
    # 着ボイス .mld 非対応機種
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
    # JPEG 非対応機種の一覧（今後の機種は対応）
    # P503i は対応だが、一部にバグがあるため、非対応とみなす
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
    # iモーション：FOMAのうちMP4非対応機種一覧
    my $DOCOMO_NO_MP4 = [qw(
        N2001     N2002     P2002   D2101V    P2101V
        SH2101V   T2101V
    )];
    # iモーション：FOMAのうちASF対応機種（旧形式なので決め打ち）
    my $DOCOMO_ASF = [qw( D2101V SH2101V T2101V )];

    # XHTML：FOMAのうちXHTML非対応機種
    my $DOCOMO_NO_XHTML = [qw(
        N2001     N2002     P2002   D2101V    P2101V
        SH2101V   T2101V
    )];
# -------------------------------------------------------------------- #
#   iモード対応HTMLバージョン(1.0〜3.0まで)
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
#   DOCOMOディスプレイサイズ
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

        'ISIM0101'    => '240x320',       # シミュレータII
      };
# -------------------------------------------------------------------- #
#   ezWeb コード→商品名変換表
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
    # SNC1/SNI1 を SNC1 と SNI1 に分解する
    foreach my $key ( keys %$EZWEB_NAME ) {
        next unless ( $key =~ m#/# );
        foreach my $sub ( split( "/", $key ) ) {
            $EZWEB_NAME->{$sub} = $EZWEB_NAME->{$key};
        }
    }
    # 着メロ .mmf 対応機種（自動判別に失敗する機種）
    my $EZWEB_MMF_OK = [qw(
        C313K TK11 TK03
    )];
    # au・TU-KA 地域会社自動判別
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
#   ASTEL dot.I 機種毎の既知情報（depth）
# -------------------------------------------------------------------- #
    my $ASTEL_DEPTH = {qw(
        AJ-51   2
    )};                                 # 機種ごとの depth
# -------------------------------------------------------------------- #
#   DDI ポケット PメールDX 色数情報（depth）
# -------------------------------------------------------------------- #
    my $PDX_DEPTH = {
        "G2"   =>  1,
        "C4"   =>  2,
        "C256" =>  8,
        "CF"   => 16,
    };                                  # 色数情報ごとの depth 変換
# -------------------------------------------------------------------- #
sub phone_info {

#   ブラウザ名、J-PHONE 識別、ezWeb 識別環境変数
    my $agent  = $ENV{HTTP_USER_AGENT};
    my $accept = $ENV{HTTP_ACCEPT};

#   ブラウザ情報を格納するハッシュ
    my $phone = {};
    $phone->{agent} = $agent;

#   ファイルタイプ対応状況

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

# ●Vodafone 3G携帯の HTTP_USER_AGENT
#   Vodafone/1.0/V702NK/NKJ001 Series60/2.6 Nokia6630/2.39.148 Profile/MID ...
#   Vodafone/1.0/V802SE/SEJ001 Browser/SEMC-Browser/4.1 Profile/MIDP-2.0 ...
#   Vodafone/1.0/V802SH/SHJ001 Browser/UP.Browser/7.0.2.1 Profile/MIDP-2.0 ...
#   Vodafone/1.0/V902SH/SHJ001 Browser/UP.Browser/7.0.2.1 Profile/MIDP-2.0 ...
#   MOT-V980/80.2F.2E. MIB/2.2.1 Profile/MIDP-2.0 Configuration/CLDC-1.1
# ●Vodafone 3G携帯のルートドキュメント(HTMLファイル)の容量制限
#   V702MO、V702sMO 10 Kbytes
#   V802N           21103 bytes
#   V902SH、V802SH  22 kbytes
#   V802SE          30kbytes
# ●ただし、画像ファイルを含めたページ全体の容量は300KBもOK
#   http://www.sharp-mobile.com/UAProf/V802SH_J001_3g.xml
#   http://www.sharp-mobile.com/UAProf/V902SH_J001_3g.xml
#   <prf:WmlDeckSize>49152</prf:WmlDeckSize>
#   <vfx:FlashDownloadMaxSize>102400</vfx:FlashDownloadMaxSize>
#   <mms:MmsMaxMessageSize>307200</mms:MmsMaxMessageSize>

    if ( $agent =~ m#^(J-PHONE|Vodafone|J-EMULATOR|Vemulator)/#i || $ENV{HTTP_X_JPHONE_MSNAME} ) {
        my( $carrier, $ver, $name ) = split( "/", $agent );
        $ver = undef unless ( $ver =~ /[0-9\.]/ );          # バグ修正
        $name = $ENV{HTTP_X_JPHONE_MSNAME} if $ENV{HTTP_X_JPHONE_MSNAME};

        $phone->{type}   = "jphone";
        $phone->{ver}    = $ver;
        $phone->{code}   = $name;       # J-DN03_a
        $name =~ s/ .*$//;              # J-SH51 SH（メーカー名削除）
        $name =~ s/_[a-z]$//;           # J-DN03（末尾削除）
        $phone->{name}   = $name;       #
        $phone->{uid}    = &get_phone_uid_jphone();         # UID を取得する

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
            $phone->{vodafone_2g} ++;           # Vodafone 2G〜2.5G携帯
            if ( $ver < 3.0 ) {                 # ステーション非対応機種
                $phone->{disable_post} ++;      # POST禁止、GETのみ
            } else {                            # ステーション対応機種
                $phone->{image_jpeg} ++;        # JPEG対応
            }
            if ( $ver < 4.0 ) {                 # パケット非対応機種
                $phone->{cache} = 6000;         # 6KBキャッシュ
            } else {                            # パケット対応機種
                $phone->{cache} = 12000;        # 12KBキャッシュ
            }
        } else {
            $phone->{vodafone_3g} ++;           # Vodafone 3G携帯
            $phone->{cache} = 307200;           # 300KBキャッシュ(画像を含む)
        }

        $phone->{image_png}  ++;                            # 必ずPNG対応
        $phone->{audio_mmf} ||= $ENV{HTTP_X_JPHONE_SMAF};   # 16和音〜
        $phone->{audio_mmf} ||= $ENV{HTTP_X_JPHONE_SOUND};  # 4和音〜
        $phone->{sound}  = (split( /,/, $ENV{HTTP_X_JPHONE_SMAF} ))[0]; #和音数
        $phone->{java}   = $ENV{HTTP_X_JPHONE_JAVA};        # Java 対応

        # XHTML対応
        # 動画対応
        if( $phone->{vodafone_3g} || ( $phone->{name} =~ m/^V80\d/ ) ) {      # 3G＋V8(W型)
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

        # KDDI-HI21 UP. Browser/6.0.2.254(GUI) MMP/1.1 ⇒ C3001H
        # UP. Browser/3.01-HI02 UP.Link/3.2.1.2        ⇒ A1000

        # 最初の / の後ろにバージョン番号が来る
        my $ver  = ( $agent =~ m#^[^\/]+\/([\d\.]+)#i )[0];
        # 最初の - の後ろに機種名が来る
        my $name = ( $agent =~ m#^[^\-]+\-([A-Z]\w+)#i )[0];

        # 製品名に %20 があれば、半角スペースに変換する
        my $prodname = $EZWEB_NAME->{$name};
        $prodname =~ s/%20/ /g;

        $phone->{type}   = "ezweb";
        $phone->{name}   = $prodname || "($name)";
        $phone->{code}   = $name;
        $phone->{color}  = ( $ecolor > 0 );
        $phone->{width}  = $width;
        $phone->{height} = $height;
        $phone->{depth}  = ( $edepth =~ /^(\d+)/ )[0];  #『16,RGB565』
        $phone->{ver}    = $ver;
        $phone->{uid}    = &get_phone_uid_ezweb();  # UID を取得する
        $phone->{image_bmp} ++;                     # 必ずBMP
        $phone->{image_png} = ( $ecolor > 0 );      # カラー機種はPNG
        $phone->{text_html} = ( $accept =~ m#text/html# );
        $phone->{text_hdml} ++;

        # (GUI) と含む機種は XHTML ネイティブ機種（2002/11/04）
        if ( $agent =~ /\(GUI\)/ ) {
            $phone->{xhtml_native} ++;
        } else {
            $phone->{hdml_native} ++;
        }

        # .mmf 対応は基本的に自動判別できるが、一部機種は自動判別できない
        my $mmf_ok = { map {$_=>1} @$EZWEB_MMF_OK };
        $phone->{audio_mmf} ++ if $mmf_ok->{$phone->{name}};
        $phone->{audio_qcp} ++ if ( $accept =~ m#audio/vnd.qcelp# );

        $phone->{image_gif} ++;                     # 最近はGIFも自動対応
        my $max_pdu = $ENV{HTTP_X_UP_DEVCAP_MAX_PDU};
        $phone->{cache} = $max_pdu if $max_pdu;

        # ＥＺ白黒機種＝容量制限の特に厳しい機種(HDML/BMP)
        $phone->{ezweb_mono} ++ if ( $max_pdu && $max_pdu < 1500 );

        # au・TU-KA 地域会社自動判別
        my $ezregex = join( "|", sort keys %$EZWEB_AREA_MAP );
        if ( $phone->{uid} =~ /^($ezregex)/ ) {
            $phone->{ezweb_area} = $EZWEB_AREA_MAP->{$1};
        }

        # EZムービー
        # 先頭の一桁が対応状況を表している
        my $ezmovie = ( $ENV{HTTP_X_UP_DEVCAP_MULTIMEDIA} =~ m/^(\d)/ )[0];
        # 仕様制限のある機種：A1302SA＝見られないとみなす
        $ezmovie = 0 if( $ezmovie == 4 );
        # 非対応なら0が入っている
        $phone->{ezmovie} = $ezmovie;

        # .amc対応
        $phone->{movie_amc}++ if( $ezmovie >= 1 && $ezmovie <= 6 );
        # .3g2対応
        $phone->{movie_3g2}++ if( $ezmovie >= 5 );

        # 動画対応
        $phone->{movie_ok}++ if( $phone->{ezmovie} );
        $phone->{voice_ok}++ if( $phone->{ezmovie} );
        # 動画サイズ
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
            ( map { $_ => 1 } @$DOCOMO_BLACK ),         # 白黒２階調
            ( map { $_ => 2 } @$DOCOMO_GLAY  ),         # グレー４階調(修正)
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
        $phone->{uid} = &get_phone_uid_docomo();        # UID を取得する
        $phone->{image_gif}  ++;                        # 必ずGIF

        my $no_mld = { map {$_=>1} @$DOCOMO_NO_MLD };   # 着信メロディ
        $phone->{audio_mld} ++ unless $no_mld->{$name}; # 基本的に対応

        my $no_voice = { map {$_=>1} @$DOCOMO_NO_VOICE };   # 着ボイス
        $phone->{docomo_voice} ++ unless $no_voice->{$name};

        my $cache = ( $sub =~ /(?:^|[^A-Za-z])c(\d+)/ )[0] * 1024;
        $phone->{cache} = $cache if $cache;
        if ( $name =~ /^[A-Z]+(50[5-9]|70[0-9]|90[0-9]|880|851)i/ ){
            $phone->{qvga} ++;                          # QVGA
        }

        # DoCoMo FOMA/PDC/PHS の区別

        if ( $name =~ /^[A-Z]+(\d{4}|9\d\di|7\d\di|880i|851i)/ ) {
            $phone->{docomo_foma} ++;                   # FOMA
        } elsif ( $name =~ /^[A-Z]+\d{3}[iI]/ ) {
            $phone->{docomo_pdc} ++;                    # PDC
        } elsif ( $name =~ /^\d{3}/ ) {
            $phone->{docomo_phs} ++;                    # PHS

        }

        # DoCoMo JPEG 対応機種の判別（2003/10/23）

        if ( $phone->{docomo_foma} ) {
            # FOMA は全機種 JPEG 対応
            $phone->{image_jpeg} ++;
        } elsif ( $phone->{docomo_pdc} ) {
            # PDC は特定機種を除いて JPEG 対応
            my $nojpeg_map = { map {$_=>1} @$DOCOMO_NO_JPEG };
            $phone->{image_jpeg} ++ unless $nojpeg_map->{$name};
        }

        # iモード対応HTMLバージョン

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

        # iモード絵文字
        # docomo_std_emojiが偽なら、拡張絵文字機種と判定できる

        if ( $ihtmlv && $ihtmlv < 4.0 ) {
            $phone->{docomo_std_emoji} ++;  # 標準絵文字機種
        }

        # ディスプレイサイズを調べる
        if( $DOCOMO_DISPLAY->{$phone->{name}} =~ m/^(.+?)x(.+?)$/ ) {
            $phone->{width}  = $1;
            $phone->{height} = $2;
        }

        # iモードシュミレータ7.0は、16ドットフォント利用とみなす
        if ( $phone->{name} eq "ISIM70" &&
             ! defined $phone->{width} &&
             $sub =~ /(?:^|\W)W(\d+)H(\d+)(?:\W|$)/ ) {
            my( $width, $height ) = ( $1, $2 );
            if ( $width <= 30 && $height <= 20 ) {
                $phone->{width}  = $1 *  8;
                $phone->{height} = $2 * 16;
            }
        }

        # XHTML対応
        if( $phone->{docomo_foma} ) {
            my $no_xhtml = { map {$_=>1} @$DOCOMO_NO_XHTML };       # FOMAのうちXHMTL非対応のもの
            $phone->{xhtml_native}++ unless( $no_xhtml->{$name} );  # FOMAは基本的に対応
        }

        # iモーション
        if( $phone->{docomo_foma} ) {
            # mp4
            my $no_mp4 = { map {$_=>1} @$DOCOMO_NO_MP4 };   # FOMAのうちMP4非対応のもの
            unless( $no_mp4->{$name} ) {                    # FOMAは基本的に対応
                $phone->{movie_ok}++;
                $phone->{voice_ok}++;
                $phone->{movie_mp4}++;
                $phone->{movie_qcif}++;
                $phone->{movie_sub_qcif}++;
            }
            # asf
            my $asf = { map {$_=>1} @$DOCOMO_ASF };         # FOMAのうちASF対応のもの
            if( $asf->{$name} ) {
                # $phone->{movie_ok}++;                     # 15秒しか再生できないらしいので非対応としておく
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
        $phone->{image_gif} ++;                 # 必ずGIF
        $phone->{image_png} ++;                 # 必ずPNG
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
        $phone->{image_gif} ++;                 # 必ずGIF
        $phone->{cache} = ( $cache =~ /(?:^|[^A-Za-z])c(\d+)/ )[0] * 1024;

    } elsif ( $agent =~ m#^L-mode/#i ) {                # L-mode

        # L-mode//1.0/AT/SHAUX-W71/10240/1000
        # L-mode//1.0/AT/NTTxxxxxxxxxxxxx-000/10240/1000
        $phone->{type}   = "lmode";
        $phone->{ver} = ( $agent =~ m#//(\d+\.\d+)/# )[0];
        $phone->{image_gif} ++;                 # 必ずGIF

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

        $phone->{type}   = undef;                   # タイプ未定義
        $phone->{color}  = ! undef;                 # でもカラーかな？

    }

    if ( $phone->{width} >= 220 ) {
        $phone->{qvga} ++;                          # QVGA
    }

    if ( ! $phone->{width} && $phone->{qvga} ) {
        $phone->{width} = 240;                      # QVGA 2004/12/01
    }

    if ( $phone->{type} ) {
        $phone->{"type_".$phone->{type}} ++;        # カンタン判別
    }

    # ハッシュへの参照を返す
    $phone;
}
# -------------------------------------------------------------------- #
#   UID を取り出す
#   ただし、UIDの型チェックのみでは詐称可能のため、
#   厳密にはＧＷセンタＩＰアドレスの制限とかも必要
# -------------------------------------------------------------------- #
sub get_phone_uid_docomo {
    # ｉモードの場合は、クエリ変数 uid が 2桁の数字で始まる
    # 00 (PDC) または 01 (FOMA) を表す
    # ⇒公式サイトで uid=NULLGWDOCOMO 指定時のみ取得可能
    # 　phone.pl の実装ではさらに GET 送信時のみ取得可能
    # 　POST 送信時は取得できない（クエリを読めないため）
    my $phone_uid = ( $ENV{QUERY_STRING} =~ /(?:^|&)uid=([%\w]+)(?:&|$)/ )[0];
    $phone_uid = undef unless ( $phone_uid =~ /^\d\d\w+$/ );
    $phone_uid;
}
sub get_phone_uid_jphone {
    # Ｊフォンの場合は、環境変数 HTTP_X_JPHONE_UID を参照する
    # ＵＩＤ送信未承諾の場合は、NULL が届くかもしれない
    # ⇒uid=1&pid=XXX&sid=XXX 指定時のみ取得可能
    my $phone_uid = $ENV{HTTP_X_JPHONE_UID};
    $phone_uid = undef if ( $phone_uid eq "NULL" );
    $phone_uid;
}
sub get_phone_uid_ezweb {
    # ＥＺウェブの場合は、4桁以上の数字で始まり、
    # 必ず ezweb.ne.jp か ido.ne.jp で終わる
    # ⇒非公式サイトでも取得可能
    my $phone_uid = $ENV{HTTP_X_UP_SUBNO};
    $phone_uid = undef unless ( $phone_uid =~ /^\d{4}.*(ezweb|ido)\.ne\.jp$/i );
    $phone_uid;
}
# -------------------------------------------------------------------- #
;1;
# -------------------------------------------------------------------- #
