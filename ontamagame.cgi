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

		# ���݂̉��
		$msg .= &checkOnline($dbh, $session->param('userid'), '���񂽂܃Q�[��');

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

	my $userid = $cgi->param('userid') || $session->param('userid');
	my $gametype = $cgi->param('gametype');


	# ���񂽂܏��擾
	my %ontama = &getOntama($dbh, $userid);
	if ($ontama{'image'} && $ontama{'health'}) {
		# �摜 URL
		if ($ontama{'image'} && $tmpl->query(name => 'URL_ONTAMAIMAGE') eq 'VAR') {
			my $url = $config{'ontamaimagesurl'}.'/'.$ontama{'image'};
			$tmpl->param(URL_ONTAMAIMAGE => &convertOutput($url));
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

		my @gamemassages = ();
		if (!$ontama{'happydiff'}) {
			$msg .= '�܂��Q�[���͂ł��Ȃ��݂����ł��B';
		} elsif ($gametype == 0) {
			# ����񂯂�
			if ($tmpl->query(name => 'JANKEN') eq 'VAR') {
				$tmpl->param(JANKEN => 1);
				push(@gamemassages, $ontama{'ownername'}.'�����'.$ontama{'name'}.'�Ƃ���񂯂񏟕��ł��I');
				push(@gamemassages, '');
				push(@gamemassages, '�u����`�񂯁`��c�v');
			}

			if ($cgi->param('gu') || $cgi->param('choki') || $cgi->param('pa')) {
				@gamemassages = ();
				push(@gamemassages, '�u�ۂ���I�v');
				push(@gamemassages, '');
				my @hand = ('�O�[', '�`���L', '�p�[');
				my $userhandindex = 0;
				if ($cgi->param('gu')) {
					$userhandindex = 0;
				} elsif ($cgi->param('choki')) {
					$userhandindex = 1;
				} else {
					$userhandindex = 2;
				}
				my $userhand = $hand[$userhandindex];
				my $ontamahand = '';
				my $idx = int(rand(3));
				if ($idx == 0) {
					# ��������
					$ontama{'happy'} = &playGame($userid, $ontama{'happy'}, 1);
					$ontamahand = $userhand;
					push(@gamemassages, '���Ȃ��̎�u'.$userhand.'�v');
					push(@gamemassages, '���񂽂܂̎�u'.$ontamahand.'�v');
					push(@gamemassages, '');
					push(@gamemassages, '���������ł��I');
				} elsif ($idx == 1) {
					# ���[�U�[�̏���
					$ontama{'happy'} = &playGame($userid, $ontama{'happy'}, 3);
					my $ontamahandindex = $userhandindex + 1;
					if ($ontamahandindex > 2) {
						$ontamahandindex = 0;
					}
					$ontamahand = $hand[$ontamahandindex];
					push(@gamemassages, '���Ȃ��̎�u'.$userhand.'�v');
					push(@gamemassages, '���񂽂܂̎�u'.$ontamahand.'�v');
					push(@gamemassages, '');
					push(@gamemassages, '���Ȃ��̏����ł��I');
				} else {
					# ���[�U�[�̕���
					my $ontamahandindex = $userhandindex - 1;
					if ($ontamahandindex < 0) {
						$ontamahandindex = 2;
					}
					$ontamahand = $hand[$ontamahandindex];
					push(@gamemassages, '���Ȃ��̎�u'.$userhand.'�v');
					push(@gamemassages, '���񂽂܂̎�u'.$ontamahand.'�v');
					push(@gamemassages, '');
					push(@gamemassages, '���Ȃ��̕����ł��I');
				}

				if ($tmpl->query(name => 'USERHAND') eq 'VAR') {
					$tmpl->param(USERHAND => &convertOutput($userhand));
				}
				if ($tmpl->query(name => 'ONTAMAHAND') eq 'VAR') {
					$tmpl->param(ONTAMAHAND => &convertOutput($ontamahand));
				}
				if ($tmpl->query(name => 'JANKEN') eq 'VAR') {
					$tmpl->param(JANKEN => 0);
				}
				
				# ���������ǂ� URL
				if ($tmpl->query(name => 'URL_ONTAMAGAMERETRY') eq 'VAR') {
					my $url = 'ontamagame.cgi?gametype='.$gametype;
					if ($userid != $session->param('userid')) {
						$url .= '&userid='.$userid;
					}
					if (&isMobile) {
						$url .= '&'.$config{'sessionname'}.'='.$session->id;
					}
					$tmpl->param(URL_ONTAMAGAMERETRY => &convertOutput($url));
				}
			}

		} else {
			$msg .= '�Q�[���^�C�v���s���ł��B';
		}

		# �Q�[�����b�Z�[�W
		if ($tmpl->query(name => 'GAMEMASSAGE') eq 'LOOP') {
			my @massagevars = ();
			foreach my $line(@gamemassages) {
				my %massagevar;
				# ���
				if ($tmpl->query(name => ['GAMEMASSAGE', 'VALUE']) eq 'VAR') {
					$massagevar{'VALUE'} = &convertOutput($line);
				}
				push(@massagevars, \%massagevar);
			}
			$tmpl->param(GAMEMASSAGE => \@massagevars);
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



	} elsif ($ontama{'image'}) {
		$msg .= '���񂽂܂͎���ł܂��B';
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


#########
# ������
sub playGame($) {
	my ($userid, $happy, $happyadd) = @_;

	$happy += $happyadd * 20;
	if ($happy > 100) {
		$happy = 100;
	} elsif ($happy < 0) {
		$happy = 0;
	}

	my $sql = 
		'UPDATE ontamausers SET'.
		' happy=?,'.
		' lasttime=NOW()'.
		' where'.
		' userid=?';
	&doDB($dbh, $sql, ($happy, $userid));
	
	return $happy;
}
