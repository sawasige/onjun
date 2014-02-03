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
		# �Z�b�V���� ID
		$sid = $session->id;

		# DB �I�[�v��
		$dbh = &connectDB(1);

		# �S�n����H�ׂ�
		my $check = 0;
		if ($cgi->param('food')) {
			$check = &eatFood();
		}

		if (!$check) {
			# ���݂̉��
			$msg .= &checkOnline($dbh, $session->param('userid'), '���񂽂�');

			# ��ʕ\��
			&disp;
		}
		
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

	# USERID
	my $userid = $cgi->param('userid') || $session->param('userid');


	# ���񂽂܏��擾
	my %ontama = &getOntama($dbh, $userid);
	if ($ontama{'image'}) {
		if ($ontama{'health'}) {
			# �摜 URL
			if ($ontama{'image'} && $tmpl->query(name => 'URL_ONTAMAIMAGE') eq 'VAR') {
				my $url = $config{'ontamaimagesurl'}.'/'.$ontama{'image'};
				$tmpl->param(URL_ONTAMAIMAGE => &convertOutput($url));
			}
		} else {
			# ���S�t���O
			if ($tmpl->query(name => 'ONTAMADEAD') eq 'VAR') {
				$tmpl->param(ONTAMADEAD => 1);
			}
		}
		
		# ���񂽂܂̖��O
		if ($ontama{'name'} && $tmpl->query(name => 'ONTAMANAME') eq 'VAR') {
			$tmpl->param(ONTAMANAME => &convertOutput($ontama{'name'}));
		}

		# ������̖��O
		if ($ontama{'ownername'} && $tmpl->query(name => 'OWNERNAME') eq 'VAR') {
			$tmpl->param(OWNERNAME => &convertOutput($ontama{'ownername'}));
		}

		# USERID
		if ($userid != $session->param('userid') && $tmpl->query(name => 'USERID') eq 'VAR') {
			$tmpl->param(USERID => &convertOutput($userid));
		}
		
		# �S�n���������� URL
		if ($tmpl->query(name => 'URL_ONTAMAFOOD') eq 'VAR') {
			my $url = 'ontama.cgi?food=1';
			if ($userid != $session->param('userid')) {
				$url .= '&userid='.$userid;
			}
			if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_ONTAMAFOOD => &convertOutput($url));
		}

		# �Q�[�������� URL
		if ($tmpl->query(name => 'URL_ONTAMAGAME') eq 'VAR') {
			my $url = 'ontamagame.cgi';
			if ($userid != $session->param('userid')) {
				$url .= '?userid='.$userid;
				if (&isMobile) {
					$url .= '&'.$config{'sessionname'}.'='.$session->id;
				}
			} elsif (&isMobile) {
				$url .= '?'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_ONTAMAGAME => &convertOutput($url));
		}

		# ���񂽂܂���߂� URL
		if ($userid == $session->param('userid') && $tmpl->query(name => 'URL_DELETEONTAMA') eq 'VAR') {
			my $url = 'deleteontamaconfirm.cgi';
			if (&isMobile) {
					$url .= '?'.$config{'sessionname'}.'='.$session->id;
			}
			$tmpl->param(URL_DELETEONTAMA => &convertOutput($url));
		}
		
		# ���
		if ($tmpl->query(name => 'ONTAMASTATUS') eq 'LOOP') {
			my @status = &getOntamaStatus($dbh, $userid, %ontama);
			my @statusvars = ();
			foreach my $line(@status) {
				my %statusvar;
				# ���
				if ($tmpl->query(name => ['ONTAMASTATUS', 'VALUE']) eq 'VAR') {
					$statusvar{'VALUE'} = &convertOutput($line);
				}
				push(@statusvars, \%statusvar);
			}
			$tmpl->param(ONTAMASTATUS => \@statusvars);
		}

		# ���L
		if ($tmpl->query(name => 'ONTAMALOGS') eq 'LOOP') {
			my @ontamalogs = &selectFetchArrayRef($dbh, 'SELECT body, registtime FROM ontamalogs WHERE userid=? ORDER BY registtime DESC LIMIT 0, 5', $userid);
			my @vars = ();
			foreach my $row(@ontamalogs) {
				my ($body, $registtime) = @$row;
				my %var;
				# ���t
				if ($tmpl->query(name => ['ONTAMALOGS', 'DATE']) eq 'VAR') {
					if ($registtime =~ /^(\d{4})\-(\d{2})\-(\d{2}) /) {
						$var{'DATE'} = &convertOutput($2.'��'.$3.'��');
					}
				}
				# �{��
				if ($tmpl->query(name => ['ONTAMALOGS', 'VALUE']) eq 'VAR') {
					$var{'VALUE'} = &convertOutput($body, 1);
				}
				push(@vars, \%var);
			}
			$tmpl->param(ONTAMALOGS => \@vars);
		}
	} else {
		$msg .= '���񂽂܂͂��܂���B';
	}

	# ���b�Z�[�W�i����΁j
	if ($msg && $tmpl->query(name => 'MSG') eq 'VAR') {
		$tmpl->param(MSG => $msg);
	}
	
	print $cgi->header(-charset=>'Shift_JIS');
	print $tmpl->output;
}


################
# �S�n����������
sub eatFood() {
	my $userid = $cgi->param('userid') || $session->param('userid');
	
	my ($lastfood) = &selectFetch($dbh, 'SELECT food FROM ontamausers WHERE userid=?', ($userid));

	if ($lastfood >= 10) {
		$msg .= '�S�n����10�ȏ゠�����܂���B';
		return 0;
	} else {
		$msg .= '�S�n���������܂����B';
		$session->param('msg', $msg);
		$session->flush();
	}

	my $food = $cgi->param('food');
	if ($food > 10) {
		$food = 10;
	}
	if ($food < 0) {
		$food = 0;
	}
	if ($food) {
		my $sql = 
			'UPDATE ontamausers SET'.
			' food=food+?,'.
			' lasttime=NOW()'.
			' where'.
			' userid=?';
		&doDB($dbh, $sql, ($food, $userid));
	}

	# ��ʃ��_�C���N�g
	if (&isMobile()) {
		my $url = 'ontama.cgi?'.$config{'sessionname'}.'='.$sid;
		if ($userid != $session->param('userid')) {
			$url .= '&userid='.$userid;
		}
		print $cgi->redirect($url);
	} else {
		my $url = 'ontama.cgi';
		if ($userid != $session->param('userid')) {
			$url .= '?userid='.$userid;
		}
		print $cgi->redirect($url);
	}

	return 1;
}
