#!/usr/bin/perl -w
use strict;
use DBI;
use File::Copy;
use Fcntl ':flock';
require '/home/himatsubu/www/onjun/config.pl';


# 設定読込
my %config = &config;

# ログ出力
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
		# トピック数
		my $topiccount = &getTopicCount($dbh, $userid, 1);

		# トピックコメント数
		my $topiccommentcount = &getTopicCommentCount($dbh, $userid, 1);
		
		# メッセージ数
		my $messagecount = &getMessageCount($dbh, $userid, 1);
		
		# 総書き込み数
		my $writtencount = $topiccount + $topiccommentcount + $messagecount;
		
		# 書き込みがない日は日記の確率4分の1
		if (!$writtencount) {
			$diarypercent /= 4;
		}
		
		# 食事
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
				&writeOntamaStatus($dbh, $userid, 'ゴハンをもらいましたが食べられませんでした。');
			}
		}
		
		# 機嫌
		$happy -= $happydiff;
		if ($happy > 100) {
			$happy = 100;
		} elsif ($happy < 0) {
			$happy = 0;
		}
		
		# 健康、成長
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
		# レベルアップ
		if ($grow >= $maxgrow) {
			$sql = 'SELECT ontamaid, image FROM ontama WHERE parentid=?';
			my @ontamalist = &selectFetchArrayRef($dbh, $sql, ($ontamaid));

			if (@ontamalist) {
				my $idx = int(rand(@ontamalist + 0));
				my $ontama = $ontamalist[$idx];
				my ($newontamaid, $sourceimage) = @$ontama;

				# 画像ファイル名
				my $destimage = $userid.'_'.&getRandomString(3).'.gif';

				# 画像ファイルコピー
				unlink($config{'ontamaimagesdir'}.'/'.$image);
				copy($config{'ontamadir'}.'/'.$sourceimage, $config{'ontamaimagesdir'}.'/'.$destimage);
				chmod(0666, ($config{'ontamaimagesdir'}.'/'.$destimage));
				
				$ontamaid = $newontamaid;
				$image = $destimage;
				
				$level++;
			} else {
				# 次の成長が無ければ死亡
				$health = 0;
			}
			$grow = 0;
			$diary = '成長したよ。';
		} elsif ($health > 0 && int(rand(100)) <= $diarypercent) {
			# 日記を書く
			if (int rand(100) <= $analyzepercent) {
				# 分析
				my $type = int rand(3);
				if ($type == 0) {
					my $topiccount = &getTopicCount($dbh, $userid, 10);
					if ($topiccount >= 3) {
						$diary = '最近よくトピックたててるね。';
					} elsif ($topiccount > 0) {
						$diary = '最近ちょこちょこトピックたててるね。';
					} else {
						$diary = '最近ぜんぜんトピックたててないね。';
					}
				} elsif ($type == 1) {
					my $topiccount = &getTopicCommentCount($dbh, $userid, 10);
					my $topiccommentcount = &getTopicCommentCount($dbh, $userid, 10);
					if ($topiccount + $topiccommentcount >= 10) {
						$diary = '最近かなり書き込んだね。';
					} elsif ($topiccount + $topiccommentcount > 0) {
						$diary = '最近ちょくちょく書き込んでるね。';
					} else {
						$diary = '最近まったく書き込みがないね。どうしたの？';
					}
				} elsif ($type == 2) {
					my $topiccount = &getTopicCommentCount($dbh, $userid, 30);
					my $topiccommentcount = &getTopicCommentCount($dbh, $userid, 30);
					if ($topiccount + $topiccommentcount >= 10) {
						$diary = 'ホントよく書き込んでるね。';
					} elsif ($topiccount + $topiccommentcount > 0) {
						$diary = 'ちょくちょく書き込んでるね。';
					} else {
						$diary = 'まったく書き込みがないね。どうしたの？ 勇気を出して書き込みしてみよう！';
					}
				}
			} else {
				# スクリプト
				my @scripts = &selectFetchArrayRef($dbh, 'SELECT body FROM ontamascripts WHERE ontamaid=?', $ontamaid);
				my $idx = int(rand(@scripts + 0));
				my $script = $scripts[$idx];
				my ($body) = @$script;
				$diary = $body;
			}
		}
		
		if (!$health) {
			$diary = 'も…もうだめ…。';
		}

		if ($diary) {
			$diary .= '（'.$days.'日目）';
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


# ログ出力
&writeLog(2, 'ontamagrow.pl end.');






##########
# DB 接続
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
# DB 切断
sub disconnectDB($) {
	my $dbh = shift;
	$dbh->disconnect()
		or die("$DBI::err:$DBI::errstr");
}

################
# DB クエリ実行
sub doDB($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	my $rv = $dbh->do($sql, undef, @bind)
		or die("$DBI::err:$DBI::errstr");
	return $rv;
}

###############################
# DB クエリを実行して値を取得
sub selectFetch($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	# 管理ユーザーを作成
	my $sth = $dbh->prepare($sql)
		or die("$DBI::err:$DBI::errstr");
	$sth->execute(@bind)
		or die("$DBI::err:$DBI::errstr");
	my @row = $sth->fetchrow_array()
		or die("$DBI::err:$DBI::errstr");
	return $row[0];
}

###############################
# DB クエリを実行して値を 1 件だけを配列で取得
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
# DB クエリを実行して値をリファレンスの配列で取得
sub selectFetchArrayRef($) {
	my $dbh = shift;
	my $sql = shift;
	my @bind = @_;
	# 管理ユーザーを作成
	my $sth = $dbh->prepare($sql);
	$sth->execute(@bind);
	my $rows = $sth->fetchall_arrayref();
	return @$rows;
}

#####################
# ランダム文字列生成
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
# ログ出力
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
		
		# ファイル書き込み
		open(OUT,">> $filename");
		flock(OUT, LOCK_EX);
		print OUT $line;
		close(OUT);
		chmod(0666, ($filename));
	}

	# 30 分の 1 の確率でガベージコレクション
	if (int(rand(30)) == 1) {
		my @files = glob($config{'logdir'}.'/*');
		foreach my $file(@files) {
			my $lastmodified = (stat $file)[9];
			# 30日間経過したファイルは削除
			if ($lastmodified < time() - 60 * 60 * 24 * 30) {
				unlink($file);
			}
		}
	}
}


##########################
# DB のおんたまの状態削除
sub deleteOntamaStatus($) {
	my ($dbh, $userid) = @_;
	# ログ出力用 SQL
	&doDB($dbh, 'DELETE FROM ontamastatus WHERE userid=?', ($userid));
}

##########################
# DB へおんたまの状態保存
sub writeOntamaStatus($) {
	&writeLog(1, 'writeOntamaStatus begin.');
	my ($dbh, $userid, $body) = @_;
	# ログ出力用 SQL
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
# おんたまの日記保存
sub writeOntamaLog($) {
	&writeLog(1, 'writeOntamaLog begin.');
	my ($dbh, $userid, $body) = @_;
	# ログ出力用 SQL
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
# トピック数
sub getTopicCount($) {
	my ($dbh, $userid, $days) = @_;
	# トピック数
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
# トピックコメント数
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
# メッセージ数
sub getMessageCount($) {
	my ($dbh, $userid, $days) = @_;
	# メッセージ数
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
