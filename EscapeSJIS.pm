# -------------------------------------------------------------------- #
#   EscapeSJIS.pm - Escape IBM extended Kanji and emoji in Shift_JIS
#   Copyright 2000-2005 Kawasaki Yuusuke <u-suke@kawa.net>
# -------------------------------------------------------------------- #
#   2000/12/18  ��ʸ����ưȽ�̡�jcode.pl Jcode.pm �б�
#   2004/10/21  Encode561.pm �б���EscapeSJIS.pm �Ȥ���ʬΥ
#   2004/10/26  mime_decode �ؿ��б���pc_emoji2image ���
#   2004/11/08  NEC �������б�
#   2004/12/01  EZweb �Ǥ�i�⡼�ɳ�ʸ���ΥХ��ʥꥳ���ɤ�Ÿ������
#   2005/02/02  Vodafone 3G���Ӥ��б�
# -------------------------------------------------------------------- #
    package EscapeSJIS;
    use strict;
    use vars qw( $VERSION );
    $VERSION = "0.01";
# -------------------------------------------------------------------- #
=head1 NAME

EscapeSJIS.pm - Escape IBM extended Kanji and emoji in Shift_JIS

=head1 SYNOPSIS

    use EscapeSJIS;
    my $text = "";
    EscapeSJIS::escape( \$text );
    EscapeSJIS::unescape( \$text, $ENV{HTTP_USER_AGENT} );
    EscapeSJIS::mime_encode( \$text );

=head1 DESCRIPTION

	escape( TEXT );

IBM ��ĥ���������ӳ�ʸ����3����ꥢ�б��ˤ�ʸ�������θ����Ȥʤ뤿�ᡢ
&#xHHHH; �������Ѵ����뤳�Ȥǡ�Shift_JIS ��ʸ�������������ˤ��ޤ���

    Windows  - IBM��ĥ������ &#xHHHH; �������Ѵ����ޤ�
    �ɥ���   - ��ʸ���� &#xHHHH; �������Ѵ����ޤ�
    Vodafone - ��ʸ���� &#xHHHH; �������Ѵ����ޤ�
    EZweb    - ��ʸ���� &#xHHHH; �������Ѵ����ޤ�

�嵭�ʳ��γ������ˤĤ��Ƥϡ����̡آ��٤��Ѵ����ޤ���
���Υ⥸�塼��Ǽ�갷��ʸ�������ɤϡ�Shift_JIS �����ɤΤߤȤ��ޤ���
EUC-JP �� UTF-8 �ؤ��Ѵ���ǽ�ϴޤߤޤ���

	unescape( TEXT, USER_AGENT );

Shift_JIS ʸ������� &#xHHHH; ������������ʬ�ˤĤ��ơ�
���ӵ��老�Ȥ�Ŭ�ڤʥХ��ʥ골ʸ�������ɤ�Ÿ�����ޤ���
�֥饦�����̤��Ȥ��������ѤǤ�������������ޤ���
�б����ʤ���ʸ���ϡ��������ޤ���

	mime_encode( TEXT )

mime_encode �ؿ��Ǥϡ��᡼��إå����Ѵ����б����ޤ���
��� unescape ������� mime_encode ��ƤӽФ��Ƥ���������
�ʤ���Jcode.pm �� mime_encode �ؿ��Ǥϳ�ʸ����Υ����ɤ�
�ޤޤ�����ʸ�����������ǽ��������ޤ���

=head1 SEE ALSO

http://www.nttdocomo.co.jp/p_s/imode/tag/emoji/list.html
http://www.dp.j-phone.com/dp/tool_dl/web/picword_01.php
http://www.au.kddi.com/ezfactory/tec/spec/3.html

=head1 COPYRIGHT

    Copyright 2004-2005 Kawasaki Yusuke <u-suke@kawa.net>

=cut
# -------------------------------------------------------------------- #
#   �ǥХå��⡼��
# -------------------------------------------------------------------- #
    my $DEBUG;
# -------------------------------------------------------------------- #
#   $DEBUG ++;
# -------------------------------------------------------------------- #
    my $SJIS_GETA  = "\x81\xAC";    # ����"��"��Shift_JIS������
    my $SJIS_SPACE = "\x81\x40";    # ���Ѷ����Shift_JIS������
    my $AMP_CREF   = "&#x%04X;";  	# &#xHHHH; �����˥���������
#   my $AMP_CREF   = "&#%05d;";  	# &#ddddd; �����˥���������
# -------------------------------------------------------------------- #
#   ����ɽ��
# -------------------------------------------------------------------- #
    my $RE_SJIS  = '[\x81-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC]';  # ����ʸ��
    my $RE_KANA  = '[\xA1-\xDF]';                       # SJISȾ�ѥ���ʸ��
    my $RE_ASCII = '[\x00-\x7F]';                       # ASCIIʸ��
    my $RE_EMOJI = '[\x84\x87\xF0-\xFC][\x40-\xFC]';    # ��ʸ������ĥ����
    my $RE_VODA  = '\x1B\x24[GEFOPQ][\x20-\x7F]+\x0F?'; # Vodafone��ʸ��
# -------------------------------------------------------------------- #
#   Shift_JIS IBM ��ĥ���� �� Unicode ���Ѵ��ޥå�
#   Encode.pm �� CP932 �ʤ��Ȥ���б����Ƥ��뤬��
#   Jcode.pm �� sjis �� IBM ��ĥ������ޤޤʤ�����
# -------------------------------------------------------------------- #
# ���� 849F��84BE
    my $EXT_KANJI_84 = [qw(
2500 2502 250C 2510 2518 2514 251C 252C 2524 2534 253C 2501 2503 250F 2513 251B
2517 2523 2533 252B 253B 254B 2520 252F 2528 2537 253F 251D 2530 2525 2538 2542
    )];
# NEC ��ĥ���� 8740��879C
    my $EXT_KANJI_87 = [qw(
2460 2461 2462 2463 2464 2465 2466 2467 2468 2469 246A 246B 246C 246D 246E 246F
2470 2471 2472 2473 2160 2161 2162 2163 2164 2165 2166 2167 2168 2169 ---- 3349
3314 3322 334D 3318 3327 3303 3336 3351 3357 330D 3326 3323 332B 334A 333B 339C
339D 339E 338E 338F 33C4 33A1 ---- ---- ---- ---- ---- ---- ---- ---- 337B ----
301D 301F 2116 33CD 2121 32A4 32A5 32A6 32A7 32A8 3231 3232 3239 337E 337D 337C
2252 2261 222B 222E 2211 221A 22A5 2220 221F 22BF 2235 2229 222A
    )];
# IBM ��ĥ���� FA40��FC4B
    my $EXT_KANJI_FA = [qw(
2170 2171 2172 2173 2174 2175 2176 2177 2178 2179 2160 2161 2162 2163 2164 2165
2166 2167 2168 2169 FFE2 FFE4 FF07 FF02 3231 2116 2121 2235 7E8A 891C 9348 9288
84DC 4FC9 70BB 6631 68C8 92F9 66FB 5F45 4E28 4EE1 4EFC 4F00 4F03 4F39 4F56 4F92
4F8A 4F9A 4F94 4FCD 5040 5022 4FFF 501E 5046 5070 5042 5094 50F4 50D8 514A ----
5164 519D 51BE 51EC 5215 529C 52A6 52C0 52DB 5300 5307 5324 5372 5393 53B2 53DD
FA0E 549C 548A 54A9 54FF 5586 5759 5765 57AC 57C8 57C7 FA0F FA10 589E 58B2 590B
5953 595B 595D 5963 59A4 59BA 5B56 5BC0 752F 5BD8 5BEC 5C1E 5CA6 5CBA 5CF5 5D27
5D53 FA11 5D42 5D6D 5DB8 5DB9 5DD0 5F21 5F34 5F67 5FB7 5FDE 605D 6085 608A 60DE
60D5 6120 60F2 6111 6137 6130 6198 6213 62A6 63F5 6460 649D 64CE 654E 6600 6615
663B 6609 662E 661E 6624 6665 6657 6659 FA12 6673 6699 66A0 66B2 66BF 66FA 670E
F929 6766 67BB 6852 67C0 6801 6844 68CF FA13 6968 FA14 6998 69E2 6A30 6A6B 6A46
6A73 6A7E 6AE2 6AE4 6BD6 6C3F 6C5C 6C86 6C6F 6CDA 6D04 6D87 6D6F
    )];
    my $EXT_KANJI_FB = [qw(
6D96 6DAC 6DCF 6DF8 6DF2 6DFC 6E39 6E5C 6E27 6E3C 6EBF 6F88 6FB5 6FF5 7005 7007
7028 7085 70AB 710F 7104 715C 7146 7147 FA15 71C1 71FE 72B1 72BE 7324 FA16 7377
73BD 73C9 73D6 73E3 73D2 7407 73F5 7426 742A 7429 742E 7462 7489 749F 7501 756F
7682 769C 769E 769B 76A6 FA17 7746 52AF 7821 784E 7864 787A 7930 FA18 FA19 ----
FA1A 7994 FA1B 799B 7AD1 7AE7 FA1C 7AEB 7B9E FA1D 7D48 7D5C 7DB7 7DA0 7DD6 7E52
7F47 7FA1 FA1E 8301 8362 837F 83C7 83F6 8448 84B4 8553 8559 856B FA1F 85B0 FA20
FA21 8807 88F5 8A12 8A37 8A79 8AA7 8ABE 8ADF FA22 8AF6 8B53 8B7F 8CF0 8CF4 8D12
8D76 FA23 8ECF FA24 FA25 9067 90DE FA26 9115 9127 91DA 91D7 91DE 91ED 91EE 91E4
91E5 9206 9210 920A 923A 9240 923C 924E 9259 9251 9239 9267 92A7 9277 9278 92E7
92D7 92D9 92D0 FA27 92D5 92E0 92D3 9325 9321 92FB FA28 931E 92FF 931D 9302 9370
9357 93A4 93C6 93DE 93F8 9431 9445 9448 9592 F9DC FA29 969D 96AF 9733 973B 9743
974D 974F 9751 9755 9857 9865 FA2A FA2B 9927 FA2C 999E 9A4E 9AD9
    )];
    my $EXT_KANJI_FC = [qw(
9ADC 9B75 9B72 9B8F 9BB1 9BBB 9C00 9D70 9D6B FA2D 9E19 9ED1
    )];
# -------------------------------------------------------------------- #
#   ������η��ӳ�ʸ���������Ѵ�����
# -------------------------------------------------------------------- #
sub escape {
    my $src = \$_[0];
    my $ref = ref $$src ? $$src : $src;     # ɬ������٥�Υ�ե����

    # ���ĤǤ� Shift_JIS�ܳ�ʸ���ܳ�ĥ������Ŭ�礷�ʤ��ѿ��������̵��
    # ��ưȽ�̤˼��Ԥ������ʤ�
    unless ( $$ref =~ /^($RE_ASCII|$RE_SJIS|$RE_KANA|
                         $RE_EMOJI|$RE_VODA)*$/s ) {
        return;
    }

    # Vodafone ��ʸ���򥨥������פ���
    my $cnt = 0;
    $cnt += ( $$ref =~ s/($RE_VODA)
                        /&one_escape_vodafone($1)||$SJIS_GETA/gex );

    # Vodafone �ʳ��γ�ʸ���ܳ�ĥʸ���򥨥������פ���
    pos() = 0;
    while ( $$ref =~ s/\G((?:$RE_ASCII|$RE_SJIS|$RE_KANA)*?)($RE_EMOJI)
                      /$1.(&one_escape_emoji($2)||$SJIS_GETA)/gex ) {
        $cnt ++;
    }

    # �Ѵ�ʸ�������֤�
    $cnt;
}
# -------------------------------------------------------------------- #
#   Shift_JIS ��� &#xHHHH; ɽ���γ�ʸ����Х��ʥ�Ÿ������
# -------------------------------------------------------------------- #
sub unescape {
    my $src = \$_[0];
    my $agent = $_[1];                      # �֥饦��̾
    my $ref = ref $$src ? $$src : $src;     # ɬ������٥�Υ�ե����

    if ( $agent =~ m#^DoCoMo/# ) {              # �ɥ����ɽ��
        $$ref =~ s/(\&\#x(E[0-9A-F]{3}|F[0-8][0-9A-F]{2});)
                  /&one_unescape_docomo($2)||$SJIS_SPACE/sigex;
    } elsif ( $agent =~ m#^(KDDI-|UP.Brows)# ) {  # EZweb��ɽ��
        $$ref =~ s/(\&\#x(E[0-9A-F]{3}|F[0-8][0-9A-F]{2});)
                  /&one_unescape_ezweb($2)||
                   &one_unescape_docomo($2)||$SJIS_SPACE/sigex;
    } elsif ( $agent =~ m#^(J-PHONE|Vodafone)/# ) {        # Vodafone��ɽ��
        $$ref =~ s/(\&\#x(E[0-9A-F]{3}|F[0-8][0-9A-F]{2});)
                  /&one_unescape_vodafone($2)||$SJIS_SPACE/sigex;
    } elsif ( $agent =~ m#^Moz# ) {             # PC��ɽ��
        $$ref =~ s/(\&\#x(E[0-9A-F]{3}|F[0-8][0-9A-F]{2});)
                  /&one_unescape_docomo($2)||$1/sigex;
    }
}
# -------------------------------------------------------------------- #
#   �᡼��� MIME �إå��ǥ�����
# -------------------------------------------------------------------- #
sub mime_decode {
    my $src = \$_[0];
    my $ref = ref $$src ? $$src : $src;     # ɬ������٥�Υ�ե����
    &require_mime_base64();                 # MIME::Base64 ���ɤ߹���
    $$ref =~ s{
        \=\?Shift_JIS\?B\?([^\s\?]+)\?\=
    }{
        MIME::Base64::decode_base64($1);
    }iegx;
}
# -------------------------------------------------------------------- #
#   �᡼��� MIME �إå����󥳡���
# -------------------------------------------------------------------- #
sub mime_encode {
    my $src = \$_[0];
    my $ref = ref $$src ? $$src : $src;     # ɬ������٥�Υ�ե����
    &require_mime_base64();                 # MIME::Base64 ���ɤ߹���
    $$ref =~ s{
        (([\x80-\x9F\xE0-\xFC][\x40-\x7E\x80-\xFC]|[\xA0-\xDF])+)
    }{
        "=?Shift_JIS?B?".MIME::Base64::encode_base64($1, "")."?=";
    }egx;
}
# -------------------------------------------------------------------- #
#   Vodafone �γ�ʸ���򥨥������פ����Ϣ³������ʸ�����б���
#   Vodafone��ʸ����1B 24 [45��51] [20��7F] 0F �� &#xF001;��&#xF539;
# -------------------------------------------------------------------- #
sub one_escape_vodafone {
    my $src = shift;
    my $str;

    if ( $src =~ /^\x1B\x24([GEFOPQ])([\x20-\x7F]+)/ ) {
        my( $high, $code ) = ( $1, $2 );

        # ����� Vodafone ��ʸ���� Unicode ��̥Х��Ȥ�
        # 0xE0 ������EZweb ��ʸ���Ȥν�ʣ���򤱤뤿�� 0xF0 �˰�ư
        my $jmap = {
            G   =>  0xF000,
            E   =>  0xF100,
            F   =>  0xF200,
            O   =>  0xF300,
            P   =>  0xF400,
            Q   =>  0xF500,
        };
        $code =~ s/(.)/sprintf($AMP_CREF,$jmap->{$high}|(ord($1)-32))/ge;
        $str = $code
    }

    $str;
}
# -------------------------------------------------------------------- #
#   Vodafone �ʳ��γ�ʸ������ĥ�����򥨥������פ���ʣ�ʸ�����ġ�
#   �ɥ��⳨ʸ������F89F��F9FC (Shift_JIS)     �� &#xE63E;��&#xE757;
#   EZweb��ʸ��1����F340��F7FC (Shift_JIS)     �� &#xE468;��&#xEB88;
#   �ɣ£ͳ�ĥ������FA40��FC4B (Shift_JIS)     �� &#x2170;��&#xFFE4;
#   ����¾�γ�������F040��F9FC�Ĥ� (Shift_JIS) �͡Ȣ��ɲ���
# -------------------------------------------------------------------- #
sub one_escape_emoji {
    my $code = unpack(n=>$_[0]) or return;
    my $str;
    if ( 0xF340 <= $code && $code <= 0xF7FC ) {         # EZweb��ʸ��
        $str = &one_escape_ezweb( $code );
    } elsif ( 0xF89F <= $code && $code <= 0xF9FC ) {    # �ɥ��⳨ʸ��
        $str = &one_escape_docomo( $code );
    } elsif (( 0x849F <= $code && $code <= 0x84BE )|| 	# ����
		     ( 0x8740 <= $code && $code <= 0x879C )||  	# NEC����
		     ( 0xFA40 <= $code && $code <= 0xFC4B )) {  # IBM��ĥ����
        $str = &one_escape_ibmext( $code );
    }
    $str;
}
# -------------------------------------------------------------------- #
#   �ɥ���γ�ʸ���ΥХ��ʥꥳ���ɤ򥨥�������(1������)
# -------------------------------------------------------------------- #
sub one_escape_docomo {
    my $sjis = shift or return;
    my $code;
    if ( $sjis >= 0xF89F && $sjis <= 0xF9FC ) {
        if ( $sjis <= 0xF8FC ) {
            $code = $sjis-4705;
        } elsif ( $sjis <= 0xF97E ) {
            $code = $sjis-4772;
        } else {
            $code = $sjis-4773;
        }
    }
    my $str = sprintf( $AMP_CREF, $code ) if $code;
    $str;
}
# -------------------------------------------------------------------- #
#   EZweb �γ�ʸ���ΥХ��ʥꥳ���ɤ򥨥�������(1������)
# -------------------------------------------------------------------- #
sub one_escape_ezweb {
    my $sjis = shift or return;
    my $code;
    if ( $sjis >= 0xF340 && $sjis <= 0xF493 ) {
        if ( $sjis <= 0xF352 ) {
            $code = $sjis-3443;
        } elsif ( $sjis <= 0xF37E ) {
            $code = $sjis-2259;
        } elsif ( $sjis <= 0xF3CE ) {
            $code = $sjis-2260;
        } elsif ( $sjis <= 0xF3FC ) {
            $code = $sjis-2241;
        } elsif ( $sjis <= 0xF47E ) {
            $code = $sjis-2308;
        } else {
            $code = $sjis-2309;
        }
    } elsif ( $sjis >= 0xF640 && $sjis <= 0xF7FC ) {
        if ( $sjis <= 0xF67E ) {
            $code = $sjis-4568;
        } elsif ( $sjis <= 0xF6FC ) {
            $code = $sjis-4569;
        } elsif ( $sjis <= 0xF77E ) {
            $code = $sjis-4636;
        } elsif ( $sjis <= 0xF7D1 ) {
            $code = $sjis-4637;
        } elsif ( $sjis <= 0xF7E4 ) {
            $code = $sjis-3287;
        } else {
            $code = $sjis-4656;
        }
    }
    my $str = sprintf( $AMP_CREF, $code ) if $code;
    $str;
}
# -------------------------------------------------------------------- #
#   �УäΣɣ£ͳ�ĥ�����ΥХ��ʥꥳ���ɤ򥨥�������(1������)
# -------------------------------------------------------------------- #
sub one_escape_ibmext {
    my $sjis = shift or return;

    my $code;                                   # �Ѵ��ޥåפ���õ��
    my( $hi, $lo ) = ( $sjis>>8, $sjis&0xFF );  # ��̤Ȳ��̤�ʬΥ
    if ( $lo < 0x40 ) {
        # ������ Shift_JIS
    } elsif ( $hi == 0x84 ) {
        $code = hex($EXT_KANJI_84->[$lo-0x9F]); # 849F��84BE
    } elsif ( $hi == 0x87 ) {
        $code = hex($EXT_KANJI_87->[$lo-0x40]); # 8740��879C
    } elsif ( $hi == 0xFA ) {
        $code = hex($EXT_KANJI_FA->[$lo-0x40]); # FA40��FAFC
    } elsif ( $hi == 0xFB ) {
        $code = hex($EXT_KANJI_FB->[$lo-0x40]); # FB40��FBFC
    } elsif ( $hi == 0xFC ) {
        $code = hex($EXT_KANJI_FC->[$lo-0x40]); # FC40��FC4B
    }

    # ��ĥ������Unicode�Ѵ��ޥåפ˥ޥå��������ϡ�����������
    my $str = sprintf( $AMP_CREF, $code ) if $code;

    $str;
}
# -------------------------------------------------------------------- #
# EZ(HDML)����ǥ��󥿤�XHTML��HDML�Ѵ���ʻ�Ѥ�����ϡ�
# Shift_JIS�Х��ʥ�����ǽ��Ϥ����Ⱦ�ѥ��ڡ����������Ƥ��ޤ���
# �������̤γ�ʸ�����֤�����äƤ��ޤ���礬����褦��
# �ɥ��⳨ʸ�����&#63647;�ٷ����ǽ��Ϥ����Ⱦ�ѥ��ڡ��������������ɤ���
#��&#xE63E;�ٷ����ϻ��ѤǤ��ʤ���
# EZ(HDML)����Ǻ�Ŭ��ɽ����Ԥ����ϡ�
# HDML�� <ICON> ���������Ѥ���Τ��٥��Ȥ�����
# -------------------------------------------------------------------- #
#   �ɥ��⳨ʸ����Shift_JIS������ɽ���ˤ�Unicodeɽ�����Ѵ�����
#   iɸ1   Shift_JIS: 63647 = F89F - Unicode: E63E (��4705)
#   iɸ94  Shift_JIS: 63740 = F8FC - Unicode: E69B (��4705)
#   iɸ95  Shift_JIS: 63808 = F940 - Unicode: E69C (��4772)
#   iɸ117 Shift_JIS: 63870 = F97E - Unicode: E6DA (��4772)
#   iɸ118 Shift_JIS: 63872 = F980 - Unicode: E6DB (��4773)
#   iɸ166 Shift_JIS: 63919 = F9AF - Unicode: E70A (��4773)
#   iɸ135 Shift_JIS: 63920 = F9B0 - Unicode: E70B (��4773)
#   i��1   Shift_JIS: 63921 = F9B1 - Unicode: E70C (��4773)
#   i��76  Shift_JIS: 63996 = F9FC - Unicode: E757 (��4773)
# -------------------------------------------------------------------- #
#   �ɥ��⳨ʸ����Shift_JIS�Х��ʥ���Ѵ�����
# -------------------------------------------------------------------- #
sub one_unescape_docomo {
    my $code = hex($_[0]) or return;
    my $sjis;
    if ( $code >= 0xE63E && $code <= 0xE757 ) {
        if ( $code <= 0xE69B ) {
            $sjis = $code+4705;
        } elsif ( $code <= 0xE6DA ) {
            $sjis = $code+4772;
        } else {
            $sjis = $code+4773;
        }
    }
    my $str = pack(n=>$sjis) if $sjis;
    $str;
}
# -------------------------------------------------------------------- #
#   Vodafone ��ʸ�� &#xE001;��&#xE539;��&#xF001;��&#xF539;
# -------------------------------------------------------------------- #
sub one_unescape_vodafone {
    my $code = hex($_[0]) or return;
    my $str;
    my $high1 = ( $code & 0xF000 );      # ���4�ӥåȤ� E �ޤ��� F
    my $high2 = ( $code & 0x0F00 ) >> 8; # �ڡ����ֹ� 1��6(�ͤ�0��5)
    my $low = $code & 0xFF;              # ����8�ӥåȤ� 01��5A

    # ��ѥ��åȵ���Ǥϡ��ڡ���1��3(�ͤ�0��2)�Τ߻��Ѳ�ǽ
    my $page3 = 1 if ( $ENV{HTTP_USER_AGENT} =~ m#^J-PHONE/[1-3]\.# );

    # �ϰ���Υ����ɤΤ��Ѵ�����
    if (( $high1 == 0xE000 || $high1 == 0xF000 ) &&
        ( $high2 < 3 || ( ! $page3 && $high2 < 6 )) &&
         $low >= 0x01 && $low <= 0x5A ) {
        # Vodafone �γ�ʸ�����ü�ʥ��������ץ�������
        my $map = [qw( G E F O P Q )];
        $str = sprintf( "\x1B\x24%s%c\x0F",$map->[$high2],$low+0x20);
    }
    $str;
}
# -------------------------------------------------------------------- #
#   EZweb ��ʸ���� 1��420��421��822 ��2�֥�å���ʬ�����
# -------------------------------------------------------------------- #

sub one_unescape_ezweb {
    my $code = hex($_[0]) or return;

    my $sjis;
    if ( $code >= 0xE468 && $code <= 0xE5DF ) {
        if ( $code <= 0xE4A6 ) {
            $sjis = $code+4568;
        } elsif ( $code <= 0xE523 ) {
            $sjis = $code+4569;
        } elsif ( $code <= 0xE562 ) {
            $sjis = $code+4636;
        } elsif ( $code <= 0xE5B4 ) {
            $sjis = $code+4637;
        } elsif ( $code <= 0xE5CC ) {
            $sjis = $code+4656;
        } else {
            $sjis = $code+3443;
        }
    } elsif ( $code >= 0xEA80 && $code <= 0xEB88 ) {
        if ( $code <= 0xEAAB ) {
            $sjis = $code+2259;
        } elsif ( $code <= 0xEAFA ) {
            $sjis = $code+2260;
        } elsif ( $code <= 0xEB0D ) {
            $sjis = $code+3287;
        } elsif ( $code <= 0xEB3B ) {
            $sjis = $code+2241;
        } elsif ( $code <= 0xEB7A ) {
            $sjis = $code+2308;
        } else {
            $sjis = $code+2309;
        }
    }
    my $str = pack(n=>$sjis) if $sjis;
    $str;
}
# -------------------------------------------------------------------- #
sub require_mime_base64 {
    if ( ! defined $MIME::Base64::VERSION ) {
        eval 'require "MIME/Base64.pm";';
    }
    if ( ! defined $MIME::Base64::VERSION ) {
        die "MIME::Base64 is required for EscapeSJIS::mime_encode()\n";
    }
}
# -------------------------------------------------------------------- #
;1; # End of the script.
# -------------------------------------------------------------------- #
