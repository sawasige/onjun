#!/usr/bin/perl -w
use strict;
use CGI::Carp qw(fatalsToBrowser); # �G���[���b�Z�[�W��\������i���Ȃ��ꍇ�R�����g�A�E�g�j
use CGI;
use CGI::Session;
use HTML::Template;
require './config.pl';
require './global.pl';
require './vars.pl';
require './jcode.pl';

my $cgi;
my %config;
my $msg;
my $session;
my $sid;

my $dbh;
my $listcount = 0;
my @list = ();
my $start = 0;
my $size = 10;

#�v���O�����J�n
&main;

##########
# ���C��
sub main {
	$cgi = new CGI;
	$msg = '';

	# �ݒ�ǂݍ���
	%config = &config;

	# �Z�b�V�����ǂݍ���
	$session = &readSession(1);
	if (defined $session) {
		$sid = $session->id;

		# DB �I�[�v��
		$dbh = &connectDB(1);

		# �ꗗ�擾
		&getList();

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '���񂽂܈ꗗ');

		# ��ʕ\��
		&disp;

		# DB �N���[�Y
		&disconnectDB($dbh);
	}
}

###########
# ��ʕ\��
sub disp {
	# �e���v���[�g�ǂݍ���
	my $tmpl = &readTemplate($cgi);

	# ���ʃe���v���[�g�ϐ��Z�b�g
	$msg .= &setCommonVars($tmpl, $session, $dbh);

	# ���b�Z�[�W
	$msg .= $session->param('msg');
	$session->clear(['msg']);
	$session->flush();
	
	# �ꗗ
	if (@list && $tmpl->query(name => 'ONTAMALIST') eq 'LOOP') {
		my @vars = ();
		foreach my $row(@list) {
			my ($userid, $name, $image, $days, $health, $ownername) = @$row;
			my %var = ();
			if ($health) {
				# �摜 URL
				if ($tmpl->query(name =>  ['ONTAMALIST', 'URL_ONTAMAIMAGE']) eq 'VAR') {
					my $url = $config{'ontamaimagesurl'}.'/'.$image;
					$var{'URL_ONTAMAIMAGE'} =  &convertOutput($url);
				}
			} else {
				# ���S�t���O
				if ($tmpl->query(name =>  ['ONTAMALIST', 'DEAD']) eq 'VAR') {
					$var{'DEAD'} = 1;
				}
			}
			# ���O
			if ($tmpl->query(name => ['ONTAMALIST', 'NAME']) eq 'VAR') {
				$var{'NAME'} = &convertOutput($name);
			}
			# ������
			if ($tmpl->query(name => ['ONTAMALIST', 'OWNERNAME']) eq 'VAR') {
				$var{'OWNERNAME'} = &convertOutput($ownername);
			}
			# ����
			if ($tmpl->query(name => ['ONTAMALIST', 'DAYS']) eq 'VAR') {
				$var{'DAYS'} = &convertOutput($days);
			}
			# ���񂽂�URL
			if ($tmpl->query(name => ['ONTAMALIST', 'ONTAMAURL']) eq 'VAR') {
				my $url = 'ontama.cgi?userid='.$userid;
				if (&isMobile()) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id();
				}
				$var{'ONTAMAURL'} = &convertOutput($url);
			}
			push(@vars, \%var);
		}
		$tmpl->param(ONTAMALIST=> \@vars);
	}

	# �O�y�[�W
	if ($start > 0 && $tmpl->query(name => 'PREVPAGEURL') eq 'VAR') {
		my $prevstart = $start - $size;
		if ($prevstart < 0) {
			$prevstart = 0;
		}
		my $url = $cgi->url(-relative=>1);
		$url .= '?start='.$prevstart;
		$url .= '&size='.$size;
		$url .= &getCondUrl();
		$tmpl->param(PREVPAGEURL => &convertOutput($url));
	}

	# �O�y�[�W�ԍ�
	if ($start > 0 && $tmpl->query(name => 'BACKPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		# 9 �y�[�W�ȏ�͈ړ��ł��Ȃ�
		my $startno = $no - 9;
		if ($startno < 1) {
			$startno = 1;
		}
		my @pagedata = ();
		for (my $i = $startno; $i <= $no - 1; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1);
			$url .= '?start='.($i-1) * $size;
			$url .= '&size='.$size;
			$url .= &getCondUrl();
			if ($tmpl->query(name => ['BACKPAGELOOP', 'BACKPAGEURL']) eq 'VAR') {
				$page{BACKPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['BACKPAGELOOP', 'BACKPAGELABEL']) eq 'VAR') {
				$page{BACKPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
		}
		$tmpl->param(BACKPAGELOOP => \@pagedata);
	}

	# ���y�[�W
	if (($start + @list) < $listcount && $tmpl->query(name => 'NEXTPAGEURL') eq 'VAR') {
		my $nextstart = $start + $size;
		my $url = $cgi->url(-relative=>1);
		$url .= '?start='.$nextstart;
		$url .= '&size='.$size;
		$url .= &getCondUrl();
		$tmpl->param(NEXTPAGEURL => &convertOutput($url));
	}

	# ���y�[�W�ԍ�
	if (($start + @list) < $listcount && $tmpl->query(name => 'FORWARDPAGELOOP') eq 'LOOP') {
		my $no = int($start / $size) + 1;
		my $maxno = int($listcount / $size);
		if ($listcount % $size) {
			$maxno++;
		}
		my @pagedata = ();
		for (my $i = $no + 1; $i <= $maxno; $i++) {
			my %page;
			my $url = $cgi->url(-relative=>1);
			$url .= '?start='.($i-1) * $size;
			$url .= '&size='.$size;
			$url .= &getCondUrl();
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGEURL']) eq 'VAR') {
				$page{FORWARDPAGEURL} = &convertOutput($url);
			}
			if ($tmpl->query(name => ['FORWARDPAGELOOP', 'FORWARDPAGELABEL']) eq 'VAR') {
				$page{FORWARDPAGELABEL} = $i;
			}
			push(@pagedata, \%page);
			# 9 �y�[�W�ȏ�͈ړ��ł��Ȃ�
			if (@pagedata >= 9) {
				last;
			}
		}
		$tmpl->param(FORWARDPAGELOOP => \@pagedata);
	}

	# ���݃y�[�W
	if ($tmpl->query(name => 'NOWPAGENOLABEL') eq 'VAR') {
		# �y�[�W��������ꍇ�����\��
		if ($size < $listcount) {
			my $no = int($start / $size) + 1;
			$tmpl->param(NOWPAGENOLABEL => $no);
		}
	}

	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}

	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}

###########################
# ���������� URL �G���R�[�h
sub getCondUrl {
	my $url = '';
	# �Z�b�V����
	if (&isMobile()) {
		$url .= '&'.$config{'sessionname'}.'='.$session->id();
	}
	return $url;
}


############
# �ꗗ�擾
sub getList() {
	$listcount = 0;
	@list = ();

	$size = $cgi->param('size') + 0;
	if (!$size) {
		$size = 10;
	}

	# �����擾
	my $sql = 
		'SELECT'.
		' COUNT(*)'.
		' FROM'.
		' ontamausers a,'.
		' users b'.
		' WHERE'.
		' a.userid=b.userid AND'.
		' b.deleteflag=?';
	my @bind = ('0');
	$listcount = &selectFetch($dbh, $sql, @bind);

	# �f�[�^������
	if ($listcount) {
		if ($cgi->param('start')) {
			$start = $cgi->param('start') + 0;
		}

		my $sql = 
			'SELECT'.
			' a.userid,'.
			' a.name,'.
			' a.image,'.
			' a.days,'.
			' a.health,'.
			' b.name'.
			' FROM'.
			' ontamausers a,'.
			' users b'.
			' WHERE'.
			' a.userid=b.userid AND'.
			' b.deleteflag=?'.
			' ORDER BY a.level DESC, a.grow DESC';
		if ($listcount >= $size) {
			$sql .= ' LIMIT '.$start.', '.$size;
		}
		my @bind = ('0');
		@list = &selectFetchArrayRef($dbh, $sql, @bind);
	}
}
