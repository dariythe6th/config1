import unittest
import os
import shutil
import tarfile
from shell_emulator import ShellEmulator


class TestShellEmulator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Создаем тестовый образ файловой системы
        cls.test_fs_path = "test_fs.tar"
        cls.test_dir = "/tmp/test_shell_fs"
        os.makedirs(cls.test_dir, exist_ok=True)

        # Добавляем тестовые файлы и директории
        with open(os.path.join(cls.test_dir, "file1.txt"), "w") as f:
            f.write("This is file1.\nLine 2.\nLine 3.\n")

        with open(os.path.join(cls.test_dir, "file2.txt"), "w") as f:
            f.write("This is file2.\n")

        os.makedirs(os.path.join(cls.test_dir, "dir1"), exist_ok=True)

        with tarfile.open(cls.test_fs_path, "w") as tar:
            tar.add(cls.test_dir, arcname="")

        # Создаем эмулятор
        cls.log_path = "test_log.xml"
        cls.shell = ShellEmulator("testuser", "localhost", cls.test_fs_path, cls.log_path)

    @classmethod
    def tearDownClass(cls):
        # Удаляем временные файлы
        shutil.rmtree(cls.test_dir)
        os.remove(cls.test_fs_path)
        os.remove(cls.log_path)

    def test_ls(self):
        # Тестирование команды ls в корневом каталоге
        self.shell.current_dir = self.shell.root_dir
        output = self.shell._cmd_ls()
        self.assertIn("file1.txt", output)
        self.assertIn("file2.txt", output)
        self.assertIn("dir1", output)

    def test_cd(self):
        # Переход в существующую директорию
        self.shell.current_dir = self.shell.root_dir
        self.shell._cmd_cd(["dir1"])
        self.assertTrue(self.shell.current_dir.endswith("dir1"))

        # Попытка перейти в несуществующую директорию
        output = self.shell._cmd_cd(["nonexistent"])
        self.assertIn("No such directory", output)

    def test_cat(self):
        # Успешный вывод содержимого файла
        output = self.shell._cmd_cat(["file1.txt"])
        self.assertIn("This is file1.", output)

        # Попытка прочитать несуществующий файл
        output = self.shell._cmd_cat(["nonexistent.txt"])
        self.assertIn("No such file", output)

    def test_tail(self):
        # Успешный вывод последних строк файла
        output = self.shell._cmd_tail(["file1.txt"])
        self.assertIn("Line 2.", output)

        # Попытка прочитать несуществующий файл
        output = self.shell._cmd_tail(["nonexistent.txt"])
        self.assertIn("No such file", output)

    def test_clear(self):
        # Очистка вывода в текстовом поле
        self.shell.text_area.insert("1.0", "Some text")
        self.shell._cmd_clear()
        self.assertEqual(self.shell.text_area.get("1.0", tk.END).strip(), "")

    def test_exit(self):
        # Тест на завершение работы (сохранение лога)
        self.shell._cmd_exit()
        self.assertTrue(os.path.exists(self.log_path))

    def test_log(self):
        # Проверка, что команды логируются в XML-файл
        self.shell._cmd_ls()
        self.shell._cmd_cd(["dir1"])
        self.shell._cmd_cat(["file1.txt"])

        # Сохранение и проверка содержимого XML
        self.shell._save_log()
        tree = ET.parse(self.log_path)
        root = tree.getroot()

        self.assertEqual(len(root.findall("action")), 3)
        for action in root.findall("action"):
            self.assertEqual(action.get("user"), "testuser")


if __name__ == "__main__":
    unittest.main()
