import re
import typing


OUTPUT_VAR = "_output_"


class Code:
    """Base class for all code item."""
    def __init__(self, text):
        self.parse(text)

    def __eq__(self, other):
        return type(self) == type(other) and repr(self) == repr(other)

    def parse(self, text: str):
        """Parse source text to internal structure"""
        raise NotImplementedError()

    def to_code(self) -> str:
        """Generate code for template function"""
        raise NotImplementedError()


class Text(Code):
    """Simple Text."""
    def parse(self, text: str):
        self._text = text

    def __repr__(self):
        return f"Text({self._text})"

    def to_code(self) -> str:
        return f"{OUTPUT_VAR}.append({repr(self._text)})"


class Expr(Code):
    """Expression in {{xxx}} format"""
    def parse(self, text: str):
        self._varname = text

    def __repr__(self):
        return f"Expr({self._varname})"

    def to_code(self) -> str:
        return f"{OUTPUT_VAR}.append(str({self._varname}))"


class Tokenizer:
    """Parse template text to tokens"""
    def tokenize(self, text: str) -> typing.List[Code]:
        segments = re.split(r'({{.*?}})', text)
        return [self.create_code(x) for x in segments]

    def create_code(self, text: str) -> Code:
        """Create code item from source text."""
        if text.startswith("{{") and text.endswith("}}"):
            return Expr(text[2:-2].strip())
        return Text(text)


class Template:
    """Render template source with context to text result."""
    def __init__(self, text: str):
        self.generate_code(text)

    def generate_code(self, source: str):
        tokenizers = Tokenizer().tokenize(source)
        code_lines = [x.to_code() for x in tokenizers]
        code = '\n'.join(code_lines)
        self._code = compile(code, '', 'exec')

    def render(self, ctx: dict = None) -> str:
        exec_ctx = (ctx or {}).copy()
        output = []
        exec_ctx[OUTPUT_VAR] = output
        exec(self._code, None, exec_ctx)
        return "".join(output)
