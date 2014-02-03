#!/usr/bin/perl -w
use strict;
use DBI;
use File::Copy;
use Fcntl ':flock';
require '/home/himatsubu/www/onjun/config.pl';


# �ݒ�Ǎ�
my %config = &config;

# ���O�o��
&writeLog(2, 'ontamagrow.pl start.');

my $dbh = &connectDB(1);

my $sql = 
	'SELECT'.
	' a.ontamaid,'.
	' a.maxgrow,'.
	' a.healthdiff,'.
	' a.hungrydiff,'.
	' a.happydiff,'.
	' a.diarypercent,'.
	' a.analyzepercent,'.
	' b.userid,'.
	' b.name,'.
	' b.image,'.
	' b.days,'.
	' b.level,'.
	' b.grow,'.
	' b.health,'.
	' b.hungry,'.
	' b.happy,'.
	' b.food,'.
	' c.name'.
	' FROM'.
	' ontama a,'.
	' ontamausers b,'.
	' users c'.
	' WHERE'.
	' a.ontamaid = b.ontamaid AND'.
	' b.userid = c.userid AND'.
	' b.growdate < SUBSTRING(NOW(), 1, 10) AND'.
	' c.deleteflag = ?';



my @ontamalist = &selectFetchArrayRef($dbh, $sql, ('0'));
my $log = sprintf("userid\tdays\thealth\tlevel\tgrow\thungry\thappy");
print $log."\n";
&writeLog(1, $log);
foreach my $row(@ontamalist) {
	my ($ontamaid, $maxgrow, $healthdiff, $hungrydiff, $happydiff, $diarypercent, $analyzepercent, $userid, $name, $image, $days, $level, $grow, $health, $hungry, $happy, $food, $ownername) = @$row;
	my $diary = '';

	&deleteOntamaStatus($dbh, $userid);

	if ($health) {
		$days++;
		# �g�s�b�N��
		my $topiccount = &getTopicCount($dbh, $userid, 1);

		# �g�s�b�N�R�����g��
		my $topiccommentcount = &getTopicCommentCount($dbh, $userid, 1);
		
		# ���b�Z�[�W��
		my $messagecount = &getMessageCount($dbh, $userid, 1);
		
		# ���������ݐ�
		my $writtencount = $topiccount + $topiccommentcount + $messagecount;
		
		# �������݂��Ȃ����͓��L�̊m��4����1
		if (!$writtencount) {
			$diarypercent /= 4;
		}
		
		# �H��
		if ($hungrydiff) {
			if ($food) {
				$hungry += $food * 30;
				$food = 0;
			} else {
				$hungry -= $hungrydiff;
			}
			if ($hungry > 100) {
				$hungry = 100;
			} elsif ($hungry < 0) {
				$hungry = 0;
			}
		} else {
			if ($food) {
				$food = 0;
				&writeOntamaStatus($dbh, $userid, '�S�n�������炢�܂������H�ׂ��܂���ł����B');
			}
		}
		
		# �@��
		$happy -= $happydiff;
		if ($happy > 100) {
			$happy = 100;
		} elsif ($happy < 0) {
			$happy = 0;
		}
		
		# ���N�A����
		if ($hungry >= 30 && $hungry < 90 && $happy >= 30) {
			$health += $healthdiff;
		}
		if ($healthdiff > 0 && ($hungry == 0 || $happy == 0)) {
			$health -= $healthdiff;
		} else {
			my $growdiff = $topiccount * 4 + $topiccommentcount * 3 + $messagecount * 3;
			if ($growdiff == 0) {
				$growdiff = 1;
			}
			$grow += ($growdiff);
		}
		if ($health > 100) {
			$health = 100;
		} elsif ($health < 0) {
			$health = 0;
		}
		# ���x���A�b�v
		if ($grow >= $maxgrow) {
			$sql = 'SELECT ontamaid, image FROM ontama WHERE parentid=?';
			my @ontamalist = &selectFetchArrayRef($dbh, $sql, ($ontamaid));

			if (@ontamalist) {
				my $idx = int(rand(@ontamalist + 0));
				my $ontama = $ontamalist[$idx];
				my ($newontamaid, $sourceimage) = @$ontama;

				# �摜�t�@�C����
				my $destimage = $userid.'_'.&getRandomString(3).'.gif';

				# �摜�t�@�C���R�s�[
				unlink($config{'ontamaimagesdir'}.'/'.$image);
				copy($config{'ontamadir'}.'/'.$sourceimage, $config{'ontamaimagesdir'}.'/'.$destimage);
				chmod(0666, ($config{'ontamaimagesdir'}.'/'.$destimage));
				
				$ontamaid = $newontamaid;
				$image = $destimage;
				
				$level++;
			} else {
				# ���̐�����������Ύ��S
				$health = 0;
			}
			$grow = 0;
			$diary = '����������B';
		} elsif ($health > 0 && int(rand(100)) <= $diarypercent) {
			# ���L������
			if (int rand(100) <= $analyzepercent) {
				# ����
				my $type = int rand(3);
				if ($type == 0) {
					my $topiccount = &getTopicCount($dbh, $userid, 10);
					if ($topiccount >= 3) {
						$diary = '�ŋ߂悭�g�s�b�N���ĂĂ�ˁB';
					} elsif ($topiccount > 0) {
						$diary = '�ŋ߂��傱���傱�g�s�b�N���ĂĂ�ˁB';
					} else {
						$diary = '�ŋ߂��񂺂�g�s�b�N���ĂĂȂ��ˁB';
					}
				} elsif ($type == 1) {
					my $topiccount = &getTopicCommentCount($dbh, $userid, 10);
					my $topiccommentcount = &getTopicCommentCount($dbh, $userid, 10);
					if ($topiccount + $topiccommentcount >= 10) {
						$diary = '�ŋ߂��Ȃ菑�����񂾂ˁB';
					} elsif ($topiccount + $topiccommentcount > 0) {
						$diary = '�ŋ߂��傭���傭��������ł�ˁB';
					} else {
						$diary = '�ŋ߂܂������������݂��Ȃ��ˁB�ǂ������́H';
					}
				} elsif ($type == 2) {
					my $topiccount = &getTopicCommentCount($dbh, $userid, 30);
					my $topiccommentcount = &getTopicCommentCount($dbh, $userid, 30);
					if ($topiccount + $topiccommentcount >= 10) {
						$diary = '�z���g�悭��������ł�ˁB';
					} elsif ($topiccount + $topiccommentcount > 0) {
						$diary = '���傭���傭��������ł�ˁB';
					} else {
						$diary = '�܂������������݂��Ȃ��ˁB�ǂ������́H �E�C���o���ď������݂��Ă݂悤�I';
					}
				}
			} else {
				# �X�N���v�g
				my @scripts = &selectFetchArrayRef($dbh, 'SELECT body FROM ontamascripts WHERE ontamaid=?', $ontamaid);
				my $idx = int(rand(@scripts + 0));
				my $script = $scripts[$idx];
				my ($body) = @$script;
				$diary = $body;
			}
		}
		
		if (!$health) {
			$diary = '���c�������߁c�B';
		}

		if ($diary) {
			$diary .= '�i'.$days.'���ځj';
			&writeOntamaLog($dbh, $userid, $diary);
			print $diary."\n";
		}

		$sql = 
			'UPDATE ontamausers SET'.
			' ontamaid = ?,'.
			' image = ?,'.
			' days = ?,'.
			' level = ?,'.
			' grow = ?,'.
			' health = ?,'.
			' hungry = ?,'.
			' happy = ?,'.
			' food = ?,'.
			' growdate = NOW(),'.
			' lasttime = NOW()'.
			' WHERE'.
			' userid = ?';
		my @bind = ($ontamaid, $image, $days, $level, $grow, $health, $hungry, $happy, $food, $userid);
		&doDB($dbh, $sql, @bind);

		$log = sprintf("$userid\t$days\t$health\t$level\t$grow\t$hungry\t$happy");
		print $log."\n";
		&writeLog(1, $log);
	
	}
}

&disconnectDB($dbh);


# ���O�o��
&writeLog(2, 'ontamagrow.pl end.');






##########
# DB �ڑ�
sub connectDB($) {
	my $raiseError = shift;
	if ($raiseError == 1) {
		$raiseError = 1;
	} else {
		$raiseError = 0;
	}
	my $dbh = DBI->connect($config{'db_source'}, $config{'db_user'}, $config{'db_pass'})
		or die("$DBI::err:$DBI::errstr");
	$dbh->{RaiseError} = $raiseError;
	return $dbh
}

##########
# DB �ؒf
sub disconnectDB($) {
	my $dbh = shift;
	$dbh->disconnect()
		or die("$DBI::err:$DBI::errstr");
}

################
# DB �N�G�����s
sub doDB($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	my $rv = $dbh->do($sql, undef, @bind)
		or die("$DBI::err:$DBI::errstr");
	return $rv;
}

###############################
# DB �N�G�������s���Ēl���擾
sub selectFetch($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	# �Ǘ����[�U�[���쐬
	my $sth = $dbh->prepare($sql)
		or die("$DBI::err:$DBI::errstr");
	$sth->execute(@bind)
		or die("$DBI::err:$DBI::errstr");
	my @row = $sth->fetchrow_array()
		or die("$DBI::err:$DBI::errstr");
	return $row[0];
}

###############################
# DB �N�G�������s���Ēl�� 1 ��������z��Ŏ擾
sub selectFetchArray($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	my $sth = $dbh->prepare($sql)
		or die("$DBI::err:$DBI::errstr".'0');
	$sth->execute(@bind)
		or die("$DBI::err:$DBI::errstr".'1');
	my @row = $sth->fetchrow_array();
	return @row;
}

#################################################
# DB �N�G�������s���Ēl�����t�@�����X�̔z��Ŏ擾
sub selectFetchArrayRef($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	# �Ǘ����[�U�[���쐬
	my $sth = $dbh->prepare($sql);
	$sth->execute(@bind);
	my $rows = $sth->fetchall_arrayref();
	return @$rows;
}

#####################
# �����_�������񐶐�
sub getRandomString($) {  #($len, $str)
  my ($len, $str) = @_;
  my @str = $str ? split //, $str : ('A'..'Z','a'..'z','0'..'9');

  undef $str;
  $len = 8 if (!$len);
  for (1 .. $len) {
    $str .= $str[int rand($#str+1)];
  }
  return $str;
}


################
# ���O�o��
sub writeLog($) {
	my ($level, $text) = @_;
	if ($level >= $config{'loglevel'}) {	
		my ($now_sec,$now_min,$now_hour,$now_mday,$now_month,$now_year,$now_wday,$now_stime) = localtime(time());
		$now_year = $now_year + 1900;
		$now_month++;
		
		
		my $time = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $now_year, $now_month, $now_mday, $now_hour, $now_min, $now_sec);
		my $filename = $config{'logdir'}.'/'.sprintf("%04d%02d%02d", $now_year, $now_month, $now_mday).'.log';
		my $useragent = $ENV{'HTTP_USER_AGENT'};
		my $remoteaddr = $ENV{'REMOTE_ADDR'};
		my $line = "$time\t$level\t$text\n";
		
		# �t�@�C����������
		open(OUT,">> $filename");
		flock(OUT, LOCK_EX);
		print OUT $line;
		close(OUT);
		chmod(0666, ($filename));
	}

	# 30 ���� 1 �̊m���ŃK�x�[�W�R���N�V����
	if (int(rand(30)) == 1) {
		my @files = glob($config{'logdir'}.'/*');
		foreach my $file(@files) {
			my $lastmodified = (stat $file)[9];
			# 30���Ԍo�߂����t�@�C���͍폜
			if ($lastmodified < time() - 60 * 60 * 24 * 30) {
				unlink($file);
			}
		}
	}
}


##########################
# DB �̂��񂽂܂̏�ԍ폜
sub deleteOntamaStatus($) {
	my ($dbh, $userid) = @_;
	# ���O�o�͗p SQL
	&doDB($dbh, 'DELETE FROM ontamastatus WHERE userid=?', ($userid));
}

##########################
# DB �ւ��񂽂܂̏�ԕۑ�
sub writeOntamaStatus($) {
	&writeLog(1, 'writeOntamaStatus begin.');
	my ($dbh, $userid, $body) = @_;
	# ���O�o�͗p SQL
	my $sql =
		'INSERT INTO ontamastatus('.
		' userid,'.
		' body,'.
		' registtime'.
		' ) VALUES ('.
		' ?,'.
		' ?,'.
		' now()'.
		' )';
	&doDB($dbh, $sql, ($userid, $body));
	&writeLog(1, 'writeOntamaStatus end.');
}

##########################
# ���񂽂܂̓��L�ۑ�
sub writeOntamaLog($) {
	&writeLog(1, 'writeOntamaLog begin.');
	my ($dbh, $userid, $body) = @_;
	# ���O�o�͗p SQL
	my $sql =
		'INSERT INTO ontamalogs('.
		' userid,'.
		' body,'.
		' registtime'.
		' ) VALUES ('.
		' ?,'.
		' ?,'.
		' now()'.
		' )';
	&doDB($dbh, $sql, ($userid, $body));
	&writeLog(1, 'writeOntamaLog end.');
}


##############
# �g�s�b�N��
sub getTopicCount($) {
	my ($dbh, $userid, $days) = @_;
	# �g�s�b�N��
	$sql = 
		'SELECT count(*)'.
		' FROM topics'.
		' WHERE'.
		' deleteflag = ?'.
		' AND registtime >= DATE_ADD(CURRENT_DATE, INTERVAL ? DAY)'.
		' AND registtime < CURRENT_DATE'.
		' AND registuserid = ?';
	my $topiccount = &selectFetch($dbh, $sql, ('0', -$days, $userid));
	return $topiccount;
}

##############
# �g�s�b�N�R�����g��
sub getTopicCommentCount($) {
	my ($dbh, $userid, $days) = @_;
	$sql = 
		'SELECT count(*)'.
		' FROM topiccomments'.
		' WHERE'.
		' deleteflag = ?'.
		' AND registtime >= DATE_ADD(CURRENT_DATE, INTERVAL ? DAY)'.
		' AND registtime < CURRENT_DATE'.
		' AND registuserid = ?';
	my $topiccommentcount = &selectFetch($dbh, $sql, ('0', -$days, $userid));
	return $topiccommentcount;
}

##############
# ���b�Z�[�W��
sub getMessageCount($) {
	my ($dbh, $userid, $days) = @_;
	# ���b�Z�[�W��
	$sql = 
		'SELECT count(*)'.
		' FROM messages'.
		' WHERE'.
		' sendtime >= DATE_ADD(CURRENT_DATE, INTERVAL ? DAY)'.
		' AND sendtime < CURRENT_DATE'.
		' AND sender_userid = ?';
	my $messagecount = &selectFetch($dbh, $sql, (-$days, $userid));
	return $messagecount;
}
