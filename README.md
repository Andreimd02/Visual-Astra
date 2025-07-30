# Visual-Astra

Visual-Astra é um simulador 3D de tomografias desenvolvido em Python utilizando VTK e NumPy. O projeto permite a visualização e manipulação de objetos, fontes e detectores em ambientes tridimensionais, simulando trajetórias e cenários típicos de experimentos de tomografia computadorizada.

## Funcionalidades
- Visualização 3D de objetos, fontes e detectores
- Simulação de trajetórias (reta e circular) para fontes e detectores
- Customização de cores e posições dos elementos
- Interface para manipulação dos parâmetros de simulação
- Utilização de arquivos de recursos gráficos (imagens, phantoms)

## Estrutura do Projeto
```
main.py                  # Arquivo principal de execução
requirements.txt         # Dependências do projeto
resources/               # Imagens e arquivos de recursos
src/                     # Código-fonte principal
    BuildFunctions.py    # Funções de construção de atores e trajetórias
    AstraCustom.py       # Customizações específicas do Astra
    interactor2d.py      # Interação 2D
    settings.py          # Configurações de cores e parâmetros
    view/                # Interface gráfica e diálogos
        Dialogs.py           # Diálogos da interface
        SimulationWindow.py   # Janela de simulação
        teste.py              # Arquivo de testes
        phantom.mat           # Phantom de exemplo
        __init__.py           # Inicialização do módulo
```

## Instalação
1. Clone o repositório:
   ```powershell
   git clone https://github.com/Andreimd02/Visual-Astra.git
   ```
2. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```

## Uso
Execute o arquivo principal:
```powershell
python main.py
```

## Requisitos
- Python 3.8+
- matplotlib
- numpy
- vtk
- PyQt5
- scipy
- scikit-image
- wheel

## Créditos
Desenvolvido por Andreimd02 e colaboradores.

## Licença
Este projeto está sob a licença MIT.
