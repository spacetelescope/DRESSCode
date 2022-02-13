import pr_comment


def test_pr_comment(capsys):
    input = "![Imgur Images](https://i.imgur.com/FbRXwrg.png),![Imgur Images](https://i.imgur.com/XdEYTIz.png),![Imgur Images](https://i.imgur.com/UO4lzz0.png),![Imgur Images](https://i.imgur.com/rZh7FOg.png),![Imgur Images](https://i.imgur.com/c5SmtXg.png),![Imgur Images](https://i.imgur.com/fLWDrAS.png)"

    expected_output = "|primary|coincidence loss|\n|:---:|:---:|\n|![Imgur Images](https://i.imgur.com/XdEYTIz.png)|![Imgur Images](https://i.imgur.com/FbRXwrg.png)|\n|![Imgur Images](https://i.imgur.com/rZh7FOg.png)|![Imgur Images](https://i.imgur.com/UO4lzz0.png)|\n|![Imgur Images](https://i.imgur.com/fLWDrAS.png)|![Imgur Images](https://i.imgur.com/c5SmtXg.png)|\n\n"

    pr_comment.main([input])
    captured = capsys.readouterr()
    assert captured.out == expected_output
