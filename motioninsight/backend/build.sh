#!/bin/bash
# Render build script — runs as root in the build container
set -euo pipefail

echo "==> Building libGLESv2.so.2 stub..."
mkdir -p libs
cat > /tmp/gles2_stub.c << 'CEOF'
/* Minimal libGLESv2.so.2 stub — all functions are no-ops.
   MediaPipe uses CPU-only inference and never calls GLES functions.
   This stub satisfies the dynamic linker dependency at load time. */
typedef unsigned int GLenum;
typedef unsigned int GLuint;
typedef int GLint;
typedef int GLsizei;
typedef unsigned char GLboolean;
typedef float GLfloat;
typedef void GLvoid;
typedef long GLintptr;
typedef long GLsizeiptr;
typedef unsigned char GLubyte;
typedef unsigned int GLbitfield;

#define V(...) __attribute__((visibility("default")))
#define S(r,f,...) V() r f(__VA_ARGS__){return(r)0;}
#define VS(f,...) V() void f(__VA_ARGS__){}

VS(glActiveTexture,GLenum a) VS(glAttachShader,GLuint a,GLuint b)
VS(glBindAttribLocation,GLuint a,GLuint b,const char*c) VS(glBindBuffer,GLenum a,GLuint b)
VS(glBindFramebuffer,GLenum a,GLuint b) VS(glBindRenderbuffer,GLenum a,GLuint b)
VS(glBindTexture,GLenum a,GLuint b) VS(glBlendColor,GLfloat a,GLfloat b,GLfloat c,GLfloat d)
VS(glBlendEquation,GLenum a) VS(glBlendEquationSeparate,GLenum a,GLenum b)
VS(glBlendFunc,GLenum a,GLenum b) VS(glBlendFuncSeparate,GLenum a,GLenum b,GLenum c,GLenum d)
VS(glBufferData,GLenum a,GLsizeiptr b,const void*c,GLenum d)
VS(glBufferSubData,GLenum a,GLintptr b,GLsizeiptr c,const void*d)
S(GLenum,glCheckFramebufferStatus,GLenum a)
VS(glClear,GLbitfield a) VS(glClearColor,GLfloat a,GLfloat b,GLfloat c,GLfloat d)
VS(glClearDepthf,GLfloat a) VS(glClearStencil,GLint a)
VS(glColorMask,GLboolean a,GLboolean b,GLboolean c,GLboolean d)
VS(glCompileShader,GLuint a)
VS(glCompressedTexImage2D,GLenum a,GLint b,GLenum c,GLsizei d,GLsizei e,GLint f,GLsizei g,const void*h)
VS(glCompressedTexSubImage2D,GLenum a,GLint b,GLint c,GLint d,GLsizei e,GLsizei f,GLenum g,GLsizei h,const void*i)
VS(glCopyTexImage2D,GLenum a,GLint b,GLenum c,GLint d,GLint e,GLsizei f,GLsizei g,GLint h)
VS(glCopyTexSubImage2D,GLenum a,GLint b,GLint c,GLint d,GLint e,GLint f,GLsizei g,GLsizei h)
S(GLuint,glCreateProgram,void) S(GLuint,glCreateShader,GLenum a)
VS(glCullFace,GLenum a) VS(glDeleteBuffers,GLsizei a,const GLuint*b)
VS(glDeleteFramebuffers,GLsizei a,const GLuint*b) VS(glDeleteProgram,GLuint a)
VS(glDeleteRenderbuffers,GLsizei a,const GLuint*b) VS(glDeleteShader,GLuint a)
VS(glDeleteTextures,GLsizei a,const GLuint*b) VS(glDepthFunc,GLenum a)
VS(glDepthMask,GLboolean a) VS(glDepthRangef,GLfloat a,GLfloat b)
VS(glDetachShader,GLuint a,GLuint b) VS(glDisable,GLenum a)
VS(glDisableVertexAttribArray,GLuint a)
VS(glDrawArrays,GLenum a,GLint b,GLsizei c)
VS(glDrawElements,GLenum a,GLsizei b,GLenum c,const void*d)
VS(glEnable,GLenum a) VS(glEnableVertexAttribArray,GLuint a)
VS(glFinish,void) VS(glFlush,void)
VS(glFramebufferRenderbuffer,GLenum a,GLenum b,GLenum c,GLuint d)
VS(glFramebufferTexture2D,GLenum a,GLenum b,GLenum c,GLuint d,GLint e)
VS(glFrontFace,GLenum a) VS(glGenBuffers,GLsizei a,GLuint*b)
VS(glGenerateMipmap,GLenum a) VS(glGenFramebuffers,GLsizei a,GLuint*b)
VS(glGenRenderbuffers,GLsizei a,GLuint*b) VS(glGenTextures,GLsizei a,GLuint*b)
VS(glGetActiveAttrib,GLuint a,GLuint b,GLsizei c,GLsizei*d,GLint*e,GLenum*f,char*g)
VS(glGetActiveUniform,GLuint a,GLuint b,GLsizei c,GLsizei*d,GLint*e,GLenum*f,char*g)
VS(glGetAttachedShaders,GLuint a,GLsizei b,GLsizei*c,GLuint*d)
S(GLint,glGetAttribLocation,GLuint a,const char*b)
VS(glGetBooleanv,GLenum a,GLboolean*b) VS(glGetBufferParameteriv,GLenum a,GLenum b,GLint*c)
S(GLenum,glGetError,void) VS(glGetFloatv,GLenum a,GLfloat*b)
VS(glGetFramebufferAttachmentParameteriv,GLenum a,GLenum b,GLenum c,GLint*d)
VS(glGetIntegerv,GLenum a,GLint*b)
VS(glGetProgramInfoLog,GLuint a,GLsizei b,GLsizei*c,char*d)
VS(glGetProgramiv,GLuint a,GLenum b,GLint*c)
VS(glGetRenderbufferParameteriv,GLenum a,GLenum b,GLint*c)
VS(glGetShaderInfoLog,GLuint a,GLsizei b,GLsizei*c,char*d)
VS(glGetShaderiv,GLuint a,GLenum b,GLint*c)
VS(glGetShaderPrecisionFormat,GLenum a,GLenum b,GLint*c,GLint*d)
VS(glGetShaderSource,GLuint a,GLsizei b,GLsizei*c,char*d)
S(const GLubyte*,glGetString,GLenum a)
VS(glGetTexParameterfv,GLenum a,GLenum b,GLfloat*c)
VS(glGetTexParameteriv,GLenum a,GLenum b,GLint*c)
VS(glGetUniformfv,GLuint a,GLint b,GLfloat*c) VS(glGetUniformiv,GLuint a,GLint b,GLint*c)
S(GLint,glGetUniformLocation,GLuint a,const char*b)
VS(glGetVertexAttribfv,GLuint a,GLenum b,GLfloat*c)
VS(glGetVertexAttribiv,GLuint a,GLenum b,GLint*c)
VS(glGetVertexAttribPointerv,GLuint a,GLenum b,void**c)
VS(glHint,GLenum a,GLenum b)
S(GLboolean,glIsBuffer,GLuint a) S(GLboolean,glIsEnabled,GLenum a)
S(GLboolean,glIsFramebuffer,GLuint a) S(GLboolean,glIsProgram,GLuint a)
S(GLboolean,glIsRenderbuffer,GLuint a) S(GLboolean,glIsShader,GLuint a)
S(GLboolean,glIsTexture,GLuint a)
VS(glLineWidth,GLfloat a) VS(glLinkProgram,GLuint a)
VS(glPixelStorei,GLenum a,GLint b) VS(glPolygonOffset,GLfloat a,GLfloat b)
VS(glReadPixels,GLint a,GLint b,GLsizei c,GLsizei d,GLenum e,GLenum f,void*g)
VS(glReleaseShaderCompiler,void)
VS(glRenderbufferStorage,GLenum a,GLenum b,GLsizei c,GLsizei d)
VS(glSampleCoverage,GLfloat a,GLboolean b)
VS(glScissor,GLint a,GLint b,GLsizei c,GLsizei d)
VS(glShaderBinary,GLsizei a,const GLuint*b,GLenum c,const void*d,GLsizei e)
VS(glShaderSource,GLuint a,GLsizei b,const char*const*c,const GLint*d)
VS(glStencilFunc,GLenum a,GLint b,GLuint c)
VS(glStencilFuncSeparate,GLenum a,GLenum b,GLint c,GLuint d)
VS(glStencilMask,GLuint a) VS(glStencilMaskSeparate,GLenum a,GLuint b)
VS(glStencilOp,GLenum a,GLenum b,GLenum c)
VS(glStencilOpSeparate,GLenum a,GLenum b,GLenum c,GLenum d)
VS(glTexImage2D,GLenum a,GLint b,GLint c,GLsizei d,GLsizei e,GLint f,GLenum g,GLenum h,const void*i)
VS(glTexParameterf,GLenum a,GLenum b,GLfloat c)
VS(glTexParameterfv,GLenum a,GLenum b,const GLfloat*c)
VS(glTexParameteri,GLenum a,GLenum b,GLint c)
VS(glTexParameteriv,GLenum a,GLenum b,const GLint*c)
VS(glTexSubImage2D,GLenum a,GLint b,GLint c,GLint d,GLsizei e,GLsizei f,GLenum g,GLenum h,const void*i)
VS(glUniform1f,GLint a,GLfloat b) VS(glUniform1fv,GLint a,GLsizei b,const GLfloat*c)
VS(glUniform1i,GLint a,GLint b) VS(glUniform1iv,GLint a,GLsizei b,const GLint*c)
VS(glUniform2f,GLint a,GLfloat b,GLfloat c) VS(glUniform2fv,GLint a,GLsizei b,const GLfloat*c)
VS(glUniform2i,GLint a,GLint b,GLint c) VS(glUniform2iv,GLint a,GLsizei b,const GLint*c)
VS(glUniform3f,GLint a,GLfloat b,GLfloat c,GLfloat d) VS(glUniform3fv,GLint a,GLsizei b,const GLfloat*c)
VS(glUniform3i,GLint a,GLint b,GLint c,GLint d) VS(glUniform3iv,GLint a,GLsizei b,const GLint*c)
VS(glUniform4f,GLint a,GLfloat b,GLfloat c,GLfloat d,GLfloat e)
VS(glUniform4fv,GLint a,GLsizei b,const GLfloat*c)
VS(glUniform4i,GLint a,GLint b,GLint c,GLint d,GLint e)
VS(glUniform4iv,GLint a,GLsizei b,const GLint*c)
VS(glUniformMatrix2fv,GLint a,GLsizei b,GLboolean c,const GLfloat*d)
VS(glUniformMatrix3fv,GLint a,GLsizei b,GLboolean c,const GLfloat*d)
VS(glUniformMatrix4fv,GLint a,GLsizei b,GLboolean c,const GLfloat*d)
VS(glUseProgram,GLuint a) VS(glValidateProgram,GLuint a)
VS(glVertexAttrib1f,GLuint a,GLfloat b) VS(glVertexAttrib1fv,GLuint a,const GLfloat*b)
VS(glVertexAttrib2f,GLuint a,GLfloat b,GLfloat c) VS(glVertexAttrib2fv,GLuint a,const GLfloat*b)
VS(glVertexAttrib3f,GLuint a,GLfloat b,GLfloat c,GLfloat d) VS(glVertexAttrib3fv,GLuint a,const GLfloat*b)
VS(glVertexAttrib4f,GLuint a,GLfloat b,GLfloat c,GLfloat d,GLfloat e) VS(glVertexAttrib4fv,GLuint a,const GLfloat*b)
VS(glVertexAttribPointer,GLuint a,GLint b,GLenum c,GLboolean d,GLsizei e,const void*f)
VS(glViewport,GLint a,GLint b,GLsizei c,GLsizei d)
CEOF

if command -v gcc > /dev/null 2>&1; then
  gcc -shared -fPIC -Wl,-soname,libGLESv2.so.2 -o libs/libGLESv2.so.2 /tmp/gles2_stub.c
  echo "==> libGLESv2.so.2 stub compiled: $(ls -lh libs/libGLESv2.so.2)"
else
  echo "==> gcc not found — stub will be downloaded at first startup"
fi

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Checking for MediaPipe pose model..."
if [ ! -f "models/pose_landmarker_full.task" ]; then
  echo "==> Downloading pose_landmarker_full.task..."
  mkdir -p models
  curl -fsSL -o models/pose_landmarker_full.task \
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task"
  echo "==> Model downloaded."
else
  echo "==> Model already present, skipping download."
fi

echo "==> Build complete."
