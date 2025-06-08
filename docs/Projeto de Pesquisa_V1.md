**Aluno(a):** Suellen Batista Dias  
**Orientador(a):**  Vinicius Santos Andrade  
**Curso:** MBA em Engenharia de Software EaD

**Atualizações automáticas de plataformas de serviços por detecção instantânea  de mudanças em especificações de API**

**Introdução**  
	  
O crescimento da chamada *Cloud Computing* é um fenômeno que vem sendo observado há mais de uma década e tem revolucionado a Tecnologia da Informação. Neste contexto, o papel dos chamados PaaS (*Platform as a Service)* ganham crescente destaque. Graças a essas tecnologias, desenvolver, hospedar e manter aplicações altamente escaláveis se tornou mais fácil e acessível.   
Diversas ferramentas digitais passam a estar disponíveis através de integrações cada vez mais simples. A necessidade de uma equipe altamente qualificada para gerir a comunicação entre sistemas diferentes vem sendo substituída por plataformas que permitem que usuários cada vez mais leigos possam criar rotinas de trabalho complexas, em alguns casos sem nenhuma linha de código.  
A Inteligência Artificial também encontra nesse tipo de plataforma um ambiente ideal para brilhar. A chamada *Agentic AI*, por exemplo, está entre as últimas tendências no mundo *Tech* e inclui agentes que planejam e executam fluxos de trabalho, assistentes pessoais e agentes de negócio com lógica autônoma. A *Agentic AI* se beneficia da integração de serviços, rapidez e escalabilidade e da abstração da infraestrutura oferecida pelos PaaS.   
O foco deste trabalho recairá sobre PaaS que oferecem acesso centralizado a vários tipos de *SaaS* (*Software as a Service*) para a geração de fluxos de ações relacionados a processos corporativos. Um desafio observado nesse contexto é acompanhar o ritmo da constante mudança dos serviços oferecidos, permitindo que os clientes possam acessar, através da plataforma, as últimas funcionalidades oferecidas pelo *SaaS*, em suas versões mais atualizadas.  
Os *SaaS* normalmente utilizam uma *API Specification*, ou *API Spec*, para definir como outros sistemas devem modelar suas requisições para que a comunicação se dê corretamente. As *API Specs* também podem informar modelos de resposta, indicações de segurança, exemplos de dados e explicação dos conceitos utilizados pelo software. Esses documentos normalmente seguem padrões reconhecidos, como o *OAS*.   
A proposta do presente estudo será, portanto, a detecção de mudanças nas *API Spec* dos serviços e a subsequente geração e disponibilização automática das novas versões para o cliente da Plataforma.

**Objetivo**

Este trabalho visa demonstrar uma alternativa para dinamizar o processo de atualização das plataformas que oferecem acesso centralizado e simplificado a diversos *SaaS*. 

**Material e Métodos**

Para demonstrar esse processo, será utilizado o tipo Pesquisa-Ação. Será desenvolvido um protótipo, ou prova de conceito, que simulará a detecção automática de mudanças na especificação da *API* de um determinado *SaaS (Github)* e enviará uma notificação à Plataforma para que esta gere uma versão compatível com as últimas atualizações.   
O desenvolvimento utilizará ferramentas como [*OpenAPI-diff*](https://github.com/OpenAPITools/openapi-diff), para monitorar as versões de *API Specs*. A partir da detecção de mudanças significativas, serão enviadas notificações à plataforma, por *webhooks*. O projeto estará escrito majoritariamente em *Python* e seguirá o padrão arquitetural orientado a eventos.   
Os processos internos e infraestrutura da plataforma serão totalmente abstraídos desta pesquisa.

**Resultados Esperados**

Espera-se implementar um sistema de detecção de mudanças nas *API Specs* dos *SaaS* que disparem notificações e agilize o processo de atualização das plataformas. 

**Cronograma de Atividades**

| Atividades planejadas | Abril | Maio | Junho | Julho | Agosto | Setembro | Outubro |
| :---- | ----- | ----- | ----- | ----- | ----- | ----- | ----- |
| Código: prototipar mecanismo de obtenção de atualizações de API Spec | 30 |  |  |  |  |  |  |
| Código: mecanismo de notificação |  | 10 |  |  |  |  |  |
| Resultados preliminares |  |  | 06 |  |  |  |  |
| Slides |  |  |  |  | 20 |  |  |
| Entrega final |  |  |  |  | 20 |  |  |
| Defesa |  |  |  |  |  |  |  |
| TCC Revisado |  |  |  |  |  |  |  |

**Referências** 

Cusumano, M. A. Cloud computing and SaaS as new computing platforms. Communications of the ACM, v. 53, n. 4, p. 27–29, 2010\. Disponível em: [https://doi.org/10.1145/1721654.1721667](https://doi.org/10.1145/1721654.1721667). Acesso em: 28 mar. 2025\.

Liu, Yuzhuo et al. Agentic AI: A Survey. \[S.l.\]: arXiv, 2023\. Disponível em: [https://arxiv.org/abs/2310.02207](https://arxiv.org/abs/2310.02207). Acesso em: 28 mar. 2025\.

Shvets, A. Dive into design patterns. \[S.l.\]: Refactoring.Guru, 2018\.

Yasrab, R. Platform-as-a-Service (PaaS): The next hype of cloud computing. ResearchGate, 2018\. Disponível em: [https://www.researchgate.net/publication/325973616\_Platform-as-a-Service\_PaaS\_The\_Next\_Hype\_of\_Cloud\_Computing](https://www.researchgate.net/publication/325973616_Platform-as-a-Service_PaaS_The_Next_Hype_of_Cloud_Computing). Acesso em: 28 mar. 2025\.

