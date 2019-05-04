FROM conda/miniconda3:latest

WORKDIR /app

COPY environment.yml ./
COPY boot.sh ./


RUN chmod +x boot.sh
RUN conda env create -f environment.yml

RUN echo "source activate essai" > ~/.bashrc
RUN conda install -c conda-forge psycopg2
RUN conda install -c conda-forge pdal
RUN apt-get update && \
    apt-get install libgl1-mesa-glx -y
RUN apt-get update && \
    apt-get install xvfb -y && \
    pip install xvfbwrapper && \
    rm -rf /root/.cache/pip/* && \
    apt-get autoremove -y && apt-get clean
RUN pip install vtk

RUN pip install sshtunnel
RUN pip install scp


COPY PDALtoVTK.py ./
COPY essai.laz ./




ENV PATH /opt/conda/envs/Modelisation/bin:$PATH


EXPOSE 80

ENTRYPOINT ["python","PDALtoVTK.py"]
