#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use HTML::Template;
use DBI;
use EscapeSJIS;
use Image::Magick;
use Fcntl ':flock';
require './config.pl';
require './global.pl';
require './vars.pl';
require './jcode.pl';

my $cgi = new CGI;
my $cginame = $cgi->url(-relative=>1); # �� ���̍s���󕶎��ɂȂ��Ă��܂�
my $tmpl = "hoge/$cginame.tmpl";

&main;

sub main() {
	print $cgi->header(-charset=>'Shift_JIS');
	print "$cginame\n";
	print "$tmpl\n";
}

0;